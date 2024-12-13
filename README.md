# IRA 🚀  
**Cyber Incident Management Reimagined - Intelligence-driven incident response**  

**IRA (Intelligent Root-cause Analyzer)** is the tool and approach you need. Designed for the high-pressure environment of **Cyber Incident Management**, IRA focuses on the **technical challenges**, helping you and your team respond effectively and decisively.  Proactive and reactive cybersecurity incident response agent.

# TL;DR   
## IRA research space

- Here's an IR report: https://docs.google.com/document/d/e/2PACX-1vTMmT84Ts8VQrEXvms3r_dIacgGtxqtK2p6wlqj3lThP8yD6LkEnz_gBhK3dIk0vmqDoHJQLje9_v8r/pub
- Here's a xAI vs DFIR report: https://docs.google.com/document/d/e/2PACX-1vRWSCS-neleLyAqem3vqssJMekVdjsfK6UQTCrifEoFiruvEHUAenffEv6egLi0bmSA9SdiCotwiL_9/pub
- Here's a xAI explainer: https://docs.google.com/document/d/e/2PACX-1vTXfZ9Gxx93JQPBb_-Pkoby40H-JxflyWSEoeceoMlNZRwhHUImSgAb-7KKLpnvS3oRTjb2cT8wMmhf/pub
- Here's a AI planner report: https://docs.google.com/document/d/e/2PACX-1vRIghXQFSCna-bIhJcYYTLdHaaImUemFTmTA5hBDdfp9t6RWPlJarG98AB8SxWcm1duCR8qeaZj3uPR/pub
- Here's a Tool AI report: https://docs.google.com/document/d/e/2PACX-1vS5yj_z0WTG-QJBVKM9jG74cdNLLInetZANyk8jIM4puylD-0mt9_TKkeaIZjdvCjnXxNz1MnOkTXW4/pub
- Here's a Microsoft DFIR report: https://docs.google.com/document/d/e/2PACX-1vQVoItBguHg3ugZTtg7u-urMIcsQeJjOcinx-lj5kG-m5MewHHdHSzP-9FaAeL-8-m_YOMQ_HX5FvE_/pub


## 🌟 Why IRA?  
There's a growing connection between XAI and computer forensics (CF), particularly as AI plays a larger role in cybersecurity and digital investigations. Here's how XAI becomes relevant in CF:

* **Understanding AI-driven tools:** CF increasingly uses AI for tasks like malware detection, anomaly identification, and image analysis. XAI helps investigators understand *why* an AI tool flagged something as suspicious, making the findings more reliable and defensible in court.

* **Explaining complex digital evidence:** Imagine an AI tool identifies a pattern of network traffic as indicative of an attack. XAI can help explain which features of that traffic led to the conclusion, providing more context and potentially uncovering the attacker's methods.

* **Building trust in digital evidence:** If AI plays a part in analyzing evidence, its conclusions might be challenged in court. XAI provides transparency, showing how the AI arrived at its findings and increasing confidence in the results.

* **Improving AI tools for CF:** By understanding how AI models work, CF specialists can refine and improve these tools, making them more effective for digital investigations.


**Think of it this way:**

* **Traditional CF:** An investigator manually examines system logs, file metadata, and network traffic to reconstruct events and find evidence.
* **AI-augmented CF:** AI tools help automate analysis, but can be "black boxes."
* **XAI-enhanced CF:** XAI adds a layer of transparency, allowing investigators to understand the AI's reasoning and use its findings more effectively.

Essentially, XAI helps bridge the gap between powerful AI capabilities and the need for human-understandable explanations in the legal and investigative context of computer forensics.

When a cyber incident strikes, technical teams focus on detecting, analyzing, and neutralizing the attackers. However, maximizing their effectiveness requires **clear communication**, **effective management**, and **focused tasking**. IRA bridges the gap between leadership and technical response teams by:  

- Ensuring the team stays focused on **remediating the incident**.  
- Helping leaders **distill critical data** for decision-making and concise briefings.  
- Providing structured frameworks for managing teams under extreme pressure.  
- Facilitating seamless communication from hands-on teams to executives and boards.  

IRA empowers teams to work like **investigative journalists**, pinpointing attackers with speed and precision, and enhances communication at all levels to ensure a coordinated response.  


## 🌟 Features

- 🧠 Multimodal Analysis: Works with diverse data types (e.g., text, logs, structured data) for comprehensive incident understanding.

- ⚡ Enhanced Efficiency: Reduces investigation time during critical incidents, minimizing downtime.

- 🔍 Heuristic-Based Retrieval: Rapidly filters relevant data and contextual information.

- 📈 MLLM-Powered Ranking: Leverages large language models across multiple data modes to rank potential causes intelligently.

- 🤝 Coordinated Team Assistance: Facilitates collaboration with AI-driven agent responses tailored to team workflows and shared insights.

- 🔧 Customizable & Scalable: Adapts to diverse system architectures and incident types.

## 🔧 Tech Stack

Languages: Python

AI Models: Multi-LLMs (customizable for domain-specific use cases)

Frameworks: Transformers, Ollama, LangChain

Tools: Docker, Pandas, PyTorch, and more

## 🌟 Your Incident Management Ally

With IRA by your side, you’ll lead with confidence, communicate effectively, and support your team to succeed in the most challenging situations.


## TODO:
- citation: https://arxiv.org/html/2410.04343v1
- citation: https://notebooklm.google/
- *** Gemini Live Voice Bidirectional API so I can talk to Agent via voice and have information show up on Laptop ***
- https://support.google.com/notebooklm/answer/15678219
- local uses tavily_search need config switch for Gemini2 uses Google Search
- generate flow charts, instructions and visual aids like pictures of instructions to go with step by step instructions (like receipes with pictures of ingredients and cooking pics)
- AI page outs and messages and voice mails with instructions and follow up info directly from agent to IR peeps 
- integration to email, sms, slack, voice
- integration to RAG - focused on tasking team, and communications. ability to upload analyse data for PII, risk analysis
- MLLM integration
- containment engine
- Preparation engine
- IR Detection and analysis engine
- Eradication engine
- Recovery engine
- Post-incident review engine
- PIA engine
- local and frontier engine. currently testing MLLM via Gemini2
- agent specific to network security ops analysis
- agent specific to network traffic analysis
- agent specific to language in network traffic and forensics analysis and exploit reconstruction and virus engine scoring
- internal speech writer? for press releases and leadership response
- AI Safety & Red Teaming training internal related to DFIR
- Hallucination Checker - GPT based 2nd opinion, 3rd Opinion?
- invent new lanaguage for turing complete, take existing implementation and rewrite in new lanaguage, new compiler for new language and deploy on hardware for encyption
- enforce human-in-the-loop agent review and approval for all activity
- documents to markdown https://github.com/microsoft/markitdown
- Policy API - manage policy 
- Data API - evaluate rules and retrieve data
- Query API - execute adhoc queries
- Compile API - access Rego’s Partial Evaluation functionality
- Health API - access instance operational health information
- Config API - view instance configuration
- Status API - view instance status state
- search api
- analysis api   ### see phi4 notebook experiments api
- communications api ### send to notebookllm api?
- document converstion api  #### experimental_api.py
- 2 stage LLM english vs french classifier API ## language_classifier-api.py
