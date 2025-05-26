# Memory Forensics & IOC Collection for Incident Response

Live Memory analysis in forensics focuses on capturing and analyzing a computer's memory (RAM) to uncover digital artifacts and evidence of compromise. Many advanced threats operate solely in memory, leaving little to no footprint on the hard drive.

## Why Memory Forensics Matters

- **Advanced persistent threats (APTs)** often operate entirely in memory
- **Fileless malware** leaves minimal disk artifacts
- **Live system state** reveals active network connections, running processes, and injected code
- **IOC extraction** enables detection of compromised systems across the environment

## Memory Acquisition Checklist

### Prerequisites
- [ ] Administrative/root privileges on target system
- [ ] Sufficient disk space (equal to system RAM size)
- [ ] Memory acquisition tool downloaded and verified
- [ ] Documentation template ready (timestamp, system info, tool version)

### Acquisition Steps
- [ ] Document system state (running processes, network connections)
- [ ] Run memory acquisition tool as administrator
- [ ] Verify dump file integrity (if tool supports it)
- [ ] Calculate and record file hash (MD5/SHA256)
- [ ] Document acquisition metadata (time, tool, operator)
- [ ] Secure transfer dump file to analysis system

## Tools & Commands

### Memory Acquisition
```bash
# WinPmem (Recommended)
winpmem.exe C:\evidence\memory_dump.raw

# DumpIt (Alternative)
DumpIt.exe

# Linux Memory Acquisition
sudo insmod lime.ko "path=/tmp/memory.lime format=lime"
```

### Volatility 3 Analysis Commands
```bash
# System Information
volatility -f memory.dump windows.info

# Process Analysis
volatility -f memory.dump windows.pslist
volatility -f memory.dump windows.pstree
volatility -f memory.dump windows.cmdline

# Network Analysis
volatility -f memory.dump windows.netscan
volatility -f memory.dump windows.netstat

# Malware Detection
volatility -f memory.dump windows.malfind
volatility -f memory.dump windows.hollowfind

# File System Analysis
volatility -f memory.dump windows.filescan
volatility -f memory.dump windows.handles

# Registry Analysis (Windows)
volatility -f memory.dump windows.registry.hivelist
volatility -f memory.dump windows.registry.printkey
```

## IOC Extraction Checklist

### Process-Based IOCs
- [ ] Suspicious process names and paths
- [ ] Unusual parent-child process relationships
- [ ] Processes with no disk backing (hollow processes)
- [ ] Injected code in legitimate processes
- [ ] Command line arguments and parameters

### Network-Based IOCs
- [ ] Unusual outbound connections
- [ ] Connections to known malicious IPs/domains
- [ ] Suspicious listening ports
- [ ] DNS queries to suspicious domains
- [ ] HTTP/HTTPS user agents

### File-Based IOCs
- [ ] Suspicious file paths and names
- [ ] Files in unusual locations
- [ ] Temporary files with random names
- [ ] Recently modified system files
- [ ] Executable files in non-executable directories

### Registry-Based IOCs (Windows)
- [ ] Persistence mechanisms (Run keys, Services)
- [ ] Modified system settings
- [ ] Unusual registry values
- [ ] Recently created registry keys
- [ ] Suspicious registry timestamps

## IOC Storage & Management

### Structured IOC Format
```json
{
  "ioc_type": "ip_address|domain|file_hash|process_name",
  "value": "192.168.1.100",
  "confidence": "high|medium|low",
  "first_seen": "2025-01-15T10:30:00Z",
  "source": "memory_analysis",
  "description": "C2 server communication",
  "tags": ["apt", "malware", "c2"]
}
```

### RAG Integration Considerations
- [ ] Standardize IOC format for consistent ingestion
- [ ] Tag IOCs with threat intelligence context
- [ ] Link related IOCs (campaign, malware family)
- [ ] Include confidence levels and source attribution
- [ ] Maintain temporal relationships between IOCs

## Analysis Workflow

### 1. Initial Triage
- [ ] System information and timeline
- [ ] Process tree analysis
- [ ] Network connections review
- [ ] Quick malware scan (malfind)

### 2. Deep Analysis
- [ ] Detailed process analysis
- [ ] Memory string analysis
- [ ] Registry examination
- [ ] File system artifacts
- [ ] Timeline reconstruction

### 3. IOC Generation
- [ ] Extract and validate IOCs
- [ ] Correlate with threat intelligence
- [ ] Document confidence levels
- [ ] Format for sharing (STIX/TAXII, JSON, CSV)

### 4. Response Actions
- [ ] Search for IOCs across environment
- [ ] Update detection rules
- [ ] Block malicious indicators
- [ ] Document lessons learned

## Best Practices

- **Speed vs. Stealth**: Balance acquisition speed with operational security
- **Chain of Custody**: Maintain detailed documentation throughout process
- **Tool Verification**: Validate tools and their integrity before use
- **Multiple Sources**: Correlate memory analysis with other forensic sources
- **Continuous Learning**: Stay updated with latest threats and techniques

## Common Volatility Plugins Reference

| Plugin | Purpose | Example Output |
|--------|---------|----------------|
| `windows.pslist` | List running processes | PID, PPID, process name, creation time |
| `windows.netscan` | Network connections | Local/remote addresses, ports, PIDs |
| `windows.malfind` | Detect injected code | Suspicious memory regions, protection flags |
| `windows.filescan` | Open file handles | File paths, PIDs, access permissions |
| `windows.cmdline` | Process command lines | Full command line arguments |

## Notes for Claude Code Integration

- Store IOCs in structured format (JSON/YAML) for easy parsing
- Use consistent tagging scheme for automated threat hunting
- Implement confidence scoring for IOC prioritization
- Consider integration with MISP or other threat intelligence platforms
- Automate common analysis workflows where possible
- https://gist.github.com/bigsnarfdude/5af050d145550fa92ed9b0d8e8beed09
- MCP V3
- https://github.com/bornpresident/Volatility-MCP-Server
- Claude Code execution tool
- https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/code-execution-tool

Resource limits
Memory: 1 GB RAM
Disk space: 5 GB workspace storage
CPU: 1 CPU
Execution timeout: Execution is limited per messages request and can be controlled with the max_execution_duration parameter
Container Expiration: After 1 hour of inactivity, the container can’t be accessed again
​

