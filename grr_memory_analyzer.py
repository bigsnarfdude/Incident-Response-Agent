import asyncio
import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import aiohttp
from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from grr_api_client import api

from incident_response_agent import graph
from configuration import Configuration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GRR Memory Analysis Pipeline")

class GRRWebhookPayload(BaseModel):
    """GRR webhook notification structure"""
    client_id: str
    flow_id: str
    event_type: str
    timestamp: str
    flow_name: str
    flow_state: str
    username: str
    client_info: Optional[Dict] = None

class MemoryAnalysisResult(BaseModel):
    """Analysis result structure"""
    client_id: str
    flow_id: str
    analysis_id: str
    timestamp: str
    volatility_results: Dict
    iocs_extracted: List[Dict]
    claude_summary: str
    risk_score: int
    recommended_actions: List[str]

class GRRMemoryAnalyzer:
    def __init__(self, grr_api_endpoint: str, grr_username: str, grr_password: str):
        self.grr_api = api.InitHttp(
            api_endpoint=grr_api_endpoint,
            auth=(grr_username, grr_password)
        )
        self.analysis_queue = asyncio.Queue()
        self.volatility_path = os.getenv("VOLATILITY_PATH", "volatility3")
        
    async def process_grr_webhook(self, payload: GRRWebhookPayload) -> Dict:
        """Process incoming GRR webhook for memory acquisition completion"""
        
        # Only process completed memory acquisition flows
        if (payload.flow_name in ["DumpProcessMemory", "ArtifactCollectorFlow"] and 
            payload.flow_state == "TERMINATED"):
            
            logger.info(f"Processing memory dump from {payload.client_id}, flow {payload.flow_id}")
            
            # Add to processing queue
            await self.analysis_queue.put({
                "client_id": payload.client_id,
                "flow_id": payload.flow_id,
                "timestamp": payload.timestamp,
                "username": payload.username
            })
            
            return {"status": "queued", "analysis_id": f"{payload.client_id}_{payload.flow_id}"}
        
        return {"status": "ignored", "reason": "Not a memory acquisition flow"}
    
    async def download_memory_dump(self, client_id: str, flow_id: str) -> Path:
        """Download memory dump from GRR flow results"""
        
        client = self.grr_api.Client(client_id)
        flow = client.Flow(flow_id)
        
        # Create temporary directory for dumps
        dump_dir = Path(tempfile.mkdtemp(prefix="grr_memory_"))
        
        # Download all memory dump files
        for result in flow.ListResults():
            if result.payload_type == "StatEntry":
                # Download the file
                output_path = dump_dir / f"memory_{client_id}_{flow_id}.raw"
                
                with open(output_path, "wb") as f:
                    file_content = result.GetFile().Read()
                    f.write(file_content)
                
                logger.info(f"Downloaded memory dump to {output_path}")
                return output_path
        
        raise ValueError(f"No memory dump found in flow {flow_id}")
    
    async def run_volatility_analysis(self, memory_path: Path) -> Dict:
        """Run Volatility plugins on memory dump"""
        
        results = {}
        
        # Define plugins to run with their purposes
        plugins = {
            "windows.info": "System information",
            "windows.pslist": "Running processes",
            "windows.pstree": "Process tree",
            "windows.netscan": "Network connections",
            "windows.malfind": "Injected code detection",
            "windows.cmdline": "Command line arguments",
            "windows.handles": "Open handles",
            "windows.filescan": "Open files",
            "windows.registry.hivelist": "Registry hives"
        }
        
        for plugin, description in plugins.items():
            try:
                logger.info(f"Running Volatility plugin: {plugin}")
                
                # Run volatility command
                cmd = [
                    self.volatility_path,
                    "-f", str(memory_path),
                    plugin,
                    "--output", "json"
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    # Parse JSON output
                    plugin_results = json.loads(result.stdout) if result.stdout else []
                    results[plugin] = {
                        "description": description,
                        "data": plugin_results,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    logger.error(f"Volatility plugin {plugin} failed: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error running {plugin}: {str(e)}")
                
        return results
    
    def extract_iocs(self, volatility_results: Dict) -> List[Dict]:
        """Extract IOCs from Volatility analysis results"""
        
        iocs = []
        
        # Extract suspicious processes
        if "windows.pslist" in volatility_results:
            for process in volatility_results["windows.pslist"]["data"]:
                # Check for suspicious process names
                suspicious_names = ["powershell", "cmd", "wscript", "cscript", "rundll32"]
                if any(sus in process.get("ImageFileName", "").lower() for sus in suspicious_names):
                    iocs.append({
                        "type": "process",
                        "value": process.get("ImageFileName"),
                        "pid": process.get("PID"),
                        "ppid": process.get("PPID"),
                        "confidence": "medium",
                        "description": "Potentially suspicious process"
                    })
        
        # Extract network connections
        if "windows.netscan" in volatility_results:
            for conn in volatility_results["windows.netscan"]["data"]:
                # Check for external connections
                foreign_addr = conn.get("ForeignAddr", "")
                if foreign_addr and not foreign_addr.startswith(("127.", "0.0.0.0", "10.", "172.", "192.168.")):
                    iocs.append({
                        "type": "ip_address",
                        "value": foreign_addr,
                        "port": conn.get("ForeignPort"),
                        "process": conn.get("Owner", {}).get("ImageFileName"),
                        "confidence": "high",
                        "description": "External network connection"
                    })
        
        # Extract injected code indicators
        if "windows.malfind" in volatility_results:
            for injection in volatility_results["windows.malfind"]["data"]:
                iocs.append({
                    "type": "code_injection",
                    "process": injection.get("Process", {}).get("ImageFileName"),
                    "pid": injection.get("Process", {}).get("PID"),
                    "protection": injection.get("Protection"),
                    "confidence": "high",
                    "description": "Possible code injection detected"
                })
        
        return iocs
    
    async def analyze_with_claude(self, client_id: str, volatility_results: Dict, iocs: List[Dict]) -> Dict:
        """Send analysis to Claude for interpretation"""
        
        # Prepare analysis request
        analysis_context = {
            "client_id": client_id,
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": volatility_results.get("windows.info", {}).get("data", {}),
            "process_count": len(volatility_results.get("windows.pslist", {}).get("data", [])),
            "network_connections": len(volatility_results.get("windows.netscan", {}).get("data", [])),
            "suspicious_processes": [ioc for ioc in iocs if ioc["type"] == "process"],
            "network_iocs": [ioc for ioc in iocs if ioc["type"] == "ip_address"],
            "code_injections": [ioc for ioc in iocs if ioc["type"] == "code_injection"]
        }
        
        # Create research topic for Claude
        research_topic = f"""Analyze this memory forensics data from client {client_id}:
        
        System has {analysis_context['process_count']} running processes and {analysis_context['network_connections']} network connections.
        
        Suspicious findings:
        - {len(analysis_context['suspicious_processes'])} suspicious processes
        - {len(analysis_context['network_iocs'])} external network connections
        - {len(analysis_context['code_injections'])} potential code injections
        
        Key IOCs detected:
        {json.dumps(iocs[:10], indent=2)}  # First 10 IOCs
        
        Provide:
        1. Threat assessment and risk score (0-100)
        2. Potential attack vectors or malware families
        3. Recommended immediate response actions
        4. Additional investigation steps
        """
        
        # Run Claude analysis
        result = await asyncio.to_thread(
            graph.invoke,
            {"research_topic": research_topic}
        )
        
        # Parse Claude's response to extract structured data
        claude_summary = result.get("running_summary", "")
        
        # Extract risk score and actions from Claude's response
        risk_score = self._extract_risk_score(claude_summary)
        recommended_actions = self._extract_actions(claude_summary)
        
        return {
            "summary": claude_summary,
            "risk_score": risk_score,
            "recommended_actions": recommended_actions,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _extract_risk_score(self, summary: str) -> int:
        """Extract risk score from Claude's summary"""
        # Simple extraction - could be improved with better parsing
        import re
        match = re.search(r'risk\s*score[:\s]*(\d+)', summary.lower())
        if match:
            return min(int(match.group(1)), 100)
        
        # Default based on keywords
        if any(word in summary.lower() for word in ["critical", "severe", "high risk"]):
            return 85
        elif any(word in summary.lower() for word in ["moderate", "medium"]):
            return 50
        else:
            return 20
    
    def _extract_actions(self, summary: str) -> List[str]:
        """Extract recommended actions from Claude's summary"""
        actions = []
        
        # Look for numbered lists or bullet points
        lines = summary.split('\n')
        for line in lines:
            if re.match(r'^\s*[\d\-\*\+]\s*', line):
                action = re.sub(r'^\s*[\d\-\*\+\.]\s*', '', line).strip()
                if action and len(action) > 10:
                    actions.append(action)
        
        return actions[:5]  # Top 5 actions
    
    async def process_analysis_queue(self):
        """Background task to process memory dumps from queue"""
        
        while True:
            try:
                # Get item from queue
                task = await self.analysis_queue.get()
                
                logger.info(f"Processing analysis task: {task}")
                
                # Download memory dump
                memory_path = await self.download_memory_dump(
                    task["client_id"],
                    task["flow_id"]
                )
                
                # Run Volatility analysis
                volatility_results = await self.run_volatility_analysis(memory_path)
                
                # Extract IOCs
                iocs = self.extract_iocs(volatility_results)
                
                # Analyze with Claude
                claude_analysis = await self.analyze_with_claude(
                    task["client_id"],
                    volatility_results,
                    iocs
                )
                
                # Create analysis result
                result = MemoryAnalysisResult(
                    client_id=task["client_id"],
                    flow_id=task["flow_id"],
                    analysis_id=f"{task['client_id']}_{task['flow_id']}",
                    timestamp=datetime.utcnow().isoformat(),
                    volatility_results=volatility_results,
                    iocs_extracted=iocs,
                    claude_summary=claude_analysis["summary"],
                    risk_score=claude_analysis["risk_score"],
                    recommended_actions=claude_analysis["recommended_actions"]
                )
                
                # Save or send results
                await self.save_analysis_results(result)
                
                # Trigger automated response if high risk
                if result.risk_score >= 70:
                    await self.trigger_automated_response(result)
                
                # Clean up temporary files
                os.unlink(memory_path)
                
            except Exception as e:
                logger.error(f"Error processing analysis: {str(e)}")
                
            finally:
                self.analysis_queue.task_done()
    
    async def save_analysis_results(self, result: MemoryAnalysisResult):
        """Save analysis results to file or database"""
        
        # Save to JSON file
        output_dir = Path("analysis_results")
        output_dir.mkdir(exist_ok=True)
        
        output_file = output_dir / f"{result.analysis_id}_{result.timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump(result.dict(), f, indent=2)
        
        logger.info(f"Saved analysis results to {output_file}")
        
        # TODO: Save to database or send to SIEM
    
    async def trigger_automated_response(self, result: MemoryAnalysisResult):
        """Trigger automated response for high-risk findings"""
        
        logger.warning(f"HIGH RISK ALERT: Client {result.client_id} scored {result.risk_score}")
        
        # Create GRR hunt for similar IOCs across fleet
        if result.iocs_extracted:
            # Create hunt for each high-confidence IOC
            for ioc in result.iocs_extracted:
                if ioc.get("confidence") == "high":
                    await self.create_ioc_hunt(ioc)
        
        # TODO: Additional automated responses
        # - Isolate system
        # - Block network IOCs at firewall
        # - Create tickets in ticketing system
        # - Send alerts to security team
    
    async def create_ioc_hunt(self, ioc: Dict):
        """Create GRR hunt for specific IOC"""
        
        try:
            if ioc["type"] == "process":
                # Hunt for process name
                hunt = self.grr_api.CreateHunt(
                    name=f"IOC_Hunt_{ioc['value']}_{datetime.utcnow().strftime('%Y%m%d')}",
                    flow_name="ListProcesses",
                    flow_args={},
                    description=f"Hunting for suspicious process: {ioc['value']}"
                )
                hunt.Start()
                
            elif ioc["type"] == "ip_address":
                # Hunt for network connections
                hunt = self.grr_api.CreateHunt(
                    name=f"IOC_Hunt_IP_{ioc['value']}_{datetime.utcnow().strftime('%Y%m%d')}",
                    flow_name="Netstat",
                    flow_args={},
                    description=f"Hunting for connections to: {ioc['value']}"
                )
                hunt.Start()
                
        except Exception as e:
            logger.error(f"Failed to create hunt for IOC {ioc}: {str(e)}")

# Initialize analyzer
analyzer = GRRMemoryAnalyzer(
    grr_api_endpoint=os.getenv("GRR_API_ENDPOINT", "http://localhost:8000"),
    grr_username=os.getenv("GRR_USERNAME", "admin"),
    grr_password=os.getenv("GRR_PASSWORD", "admin")
)

@app.post("/grr/webhook")
async def grr_webhook(payload: GRRWebhookPayload, background_tasks: BackgroundTasks):
    """Webhook endpoint for GRR notifications"""
    
    result = await analyzer.process_grr_webhook(payload)
    return JSONResponse(content=result)

@app.get("/analysis/status/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get status of a specific analysis"""
    
    # Check if analysis results exist
    results_dir = Path("analysis_results")
    matching_files = list(results_dir.glob(f"{analysis_id}_*.json"))
    
    if matching_files:
        with open(matching_files[0], "r") as f:
            return json.load(f)
    else:
        raise HTTPException(status_code=404, detail="Analysis not found")

@app.on_event("startup")
async def startup_event():
    """Start background processing task"""
    asyncio.create_task(analyzer.process_analysis_queue())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)