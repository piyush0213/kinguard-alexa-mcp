# KinGuard: Ambient Cognitive Care & Verification Protocol

[![Alexa+ Track](https://img.shields.io/badge/Alexa%2B-MCP%20Server%20(2025--11--25)-00caec.svg)](https://developer.amazon.com/alexa)
[![AWS Builder Challenge](https://img.shields.io/badge/AWS-Bedrock%20Claude%203.5%20%7C%20SNS%20%7C%20EventBridge-ff9900.svg)](https://aws.amazon.com/bedrock/)
[![Ring Verified](https://img.shields.io/badge/Ring-Doorbell%20Intercom-0ea5e9.svg)](https://ring.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

> **Grand Prize Submission for the Amazon Developer Hackathon: Build, Ship, Shape (Devpost 2026)**  
> **Primary Track:** Alexa+ (Self-Hosted MCP Server & Agent Skill)  
> **Mini-Challenges:** AWS Builder Challenge & Open Source Mini Challenge

---

## Executive Summary

Over **55 million elderly adults** worldwide live independently while coping with early-stage cognitive impairment, memory lapses, or dementia. Traditional voice assistants repeatedly fail them:
* When unfamiliar visitors knock at the front door, seniors experience acute anxiety or open the door to utility scammers and aggressive solicitors.
* When they forget whether they took their morning heart medications, they repeatedly question themselves or make panic calls to stressed family members.
* Standard assistants argue with them ("You already asked me that 5 minutes ago"), which directly violates clinical **Validation Therapy** guidelines and elevates confusion.

**KinGuard** is an ambient cognitive guardrail protocol that bridges **Alexa+**, **Ring smart doorbells**, and **Amazon Bedrock**. By deploying a self-hosted **Model Context Protocol (MCP)** server over **Streamable HTTP and Server-Sent Events (SSE)**, KinGuard equips Alexa+ with real-time verifiable home telemetry to gently ground seniors in reality, verify porch visitors, speak through the porch intercom, and keep remote family caregivers informed via **Amazon SNS**.

---

## System Architecture

```
                                 ┌─────────────────────────┐
                                 │   Elderly Resident      │
                                 │    (Martha Miller)      │
                                 └────────────┬────────────┘
                                              │ Natural Voice Query
                                              ▼
                             ┌─────────────────────────────────┐
                             │    Alexa+ Ambient Assistant     │
                             │  (Speech Synthesis / Web Mic)   │
                             └────────────────┬────────────────┘
                                              │
                      Streamable HTTP / SSE   │ (Spec 2025-11-25)
                      JSON-RPC 2.0 Over /mcp  │
                                              ▼
 ┌────────────────────────────────────────────────────────────────────────────────────────┐
 │                              KinGuard Core MCP Server                                  │
 │                                (FastAPI & Uvicorn)                                     │
 ├────────────────────────────────────────────────────────────────────────────────────────┤
 │  Declared MCP Tools:                                                                   │
 │   • kinguard_get_door_snapshot       -> Inspects Ring porch feed & AI badge detection │
 │   • kinguard_respond_door_visitor    -> 2-way TTS intercom dispatch to porch speaker   │
 │   • kinguard_verify_medication_state -> Inspects smart pill dispenser tray timestamps  │
 │   • kinguard_verify_home_safety      -> Verifies stove sensors, locks & motion vitals  │
 │   • kinguard_escalate_caregiver      -> Dispatches emergency SMS to family caregivers  │
 └─────────────────┬──────────────────────────┬─────────────────────────────┬─────────────┘
                   │                          │                             │
                   ▼                          ▼                             ▼
   ┌───────────────────────────────┐ ┌───────────────────┐ ┌─────────────────────────────┐
   │        Amazon Bedrock         │ │  Ring Porch Feed  │ │         Amazon SNS          │
   │   (Claude 3.5 Sonnet/Haiku)   │ │  & Intercom TTS   │ │   & Custom EventBridge Bus  │
   │  Enforces Clinical Validation │ │ Live camera HUD   │ │ Dispatches SMS to caregiver │
   │  Therapy & Ambient Grounding  │ │ & 2-way intercom  │ │ (Sarah Miller: 555-019-2831)│
   └───────────────────────────────┘ └───────────────────┘ └─────────────────────────────┘
```

---

## Core Capabilities

### 1. Context-Aware Ring Doorbell Escort
* When someone knocks or rings the chime, Martha simply asks: *"Alexa, who is at the front door?"*
* KinGuard calls `kinguard_get_door_snapshot` via MCP:
  * **Verified Courier:** Confirms Amazon Prime Logistics delivery with parcel ID, reassures Martha that the deadbolt is securely locked, and offers to have the parcel placed on the porch.
  * **Unverified Stranger:** Identifies uncredentialed solicitors, reassures Martha that she is safe inside, and offers to take a message through the intercom.
  * **Friendly Neighbor:** Detects verified neighbor Tom Higgins, providing familiar reassurance.
* Martha responds: *"Tell them to leave it on the porch."* Alexa+ dispatches `kinguard_respond_door_visitor`, broadcasting a calming synthesized TTS voice through the Ring porch speaker: *"Please leave the parcel by the front door. Martha is resting inside. Thank you!"*

### 2. Ambient Medication Grounding
* Martha asks: *"Did I take my blood pressure pills today?"*
* Instead of hallucinating, KinGuard executes `kinguard_verify_medication_state` to inspect the smart pill dispenser tray:
  * **If Taken:** *"Yes Martha, you're all set! You took your Metoprolol at 9:00 AM this morning with water. Your next scheduled dose is Donepezil tonight at dinner."*
  * **If Missed:** *"Martha, I checked your smart pill tray, and your morning Metoprolol is still waiting. Let's take it together right now with a fresh glass of water."*

### 3. Clinical Validation Therapy via Amazon Bedrock
* Powered by `anthropic.claude-3-haiku` / `claude-3-5-sonnet` on Amazon Bedrock.
* Never invalidates emotion, never argues, and never says "You already asked that".
* Generates concise, warm, 1–2 sentence vocal guidance designed to lower cortisol and anxiety.

### 4. Amazon SNS & EventBridge Caregiver Escalation
* When high-anxiety panic loops or security alerts occur, KinGuard calls `kinguard_escalate_caregiver`.
* Publishes structured events to an Amazon EventBridge custom bus and sends an immediate SMS notification to Martha's daughter Sarah (+1-555-019-2831).

---

## Hackathon Track & Challenge Alignment

| Category | Requirement | KinGuard Implementation |
| :--- | :--- | :--- |
| **Primary Track: Alexa+** | Self-hosted MCP Server (Spec 2025-11-25+, Streamable HTTP) or Agent Skill | Full JSON-RPC 2.0 MCP server over Streamable HTTP (`POST /mcp`) and SSE (`GET /mcp/sse`), plus integrated Alexa+ Agent Skill runner with live Web Speech synthesis & mic recognition. |
| **Mini Challenge: AWS Builder** | Integration with AWS Bedrock, AgentCore, Strands, SNS, EventBridge | Uses Amazon Bedrock (Claude 3.5 Sonnet / Haiku), Amazon SNS for caregiver SMS pushes, Amazon EventBridge for event auditing, and includes CloudFormation IaC template (`cloudformation_stack.yaml`). |
| **Mini Challenge: Open Source** | New open-source repository with open source license | Released publicly on GitHub under the permissive MIT License with full documentation and reproducible tests. |
| **Judging Bonus (+10%)** | Product Feedback & Friction Logs | Exhaustive feedback on Alexa+ MCP, Bedrock, Ring APIs, and 4 detailed Friction Logs in [`PRODUCT_FEEDBACK_AND_FRICTION_LOG.md`](PRODUCT_FEEDBACK_AND_FRICTION_LOG.md). |

---

## Repository Structure

```
kinguard/
├── aws_integration/
│   ├── bedrock_cognitive_engine.py   # Amazon Bedrock Claude 3.5 validation therapy engine
│   ├── sns_dispatcher.py             # Amazon SNS & EventBridge caregiver alert dispatcher
│   └── cloudformation_stack.yaml     # CloudFormation IaC template for AWS services
├── mcp_server/
│   ├── kinguard_mcp.py               # Standalone MCP Streamable HTTP / SSE server (JSON-RPC)
│   ├── alexa_skill_agent.py          # Alexa+ Agent Skill intent router & Bedrock glue
│   └── state_store.py                # Ambient IoT state engine (Door, Meds, Stove, Vitals)
├── simulator/
│   ├── simulator_server.py           # Integrated FastAPI backend with REST & MCP endpoints
│   └── static/
│       └── index.html                # High-fidelity interactive web dashboard with speech & canvas
├── run.py                            # Main Python launcher
├── start.bat                         # 1-click Windows runner
├── requirements.txt                  # Python dependencies
├── LICENSE                           # Open Source MIT License
├── PRODUCT_FEEDBACK_AND_FRICTION_LOG.md # Developer product feedback & friction logs
└── README.md                         # Project documentation
```

---

## Quickstart & Installation

### Prerequisites
* Python 3.10 or higher
* Modern web browser (Chrome, Edge, Safari, or Firefox)

### 1. Clone the Repository
```bash
git clone https://github.com/piyush0213/kinguard-alexa-mcp.git
cd kinguard-alexa-mcp
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
Double-click `start.bat` on Windows, or run:
```bash
python run.py
```

Open your browser to:
👉 **`http://127.0.0.1:8080`**

---

## Interactive Demo Features in Web Simulator

1. **Ring Porch Security Camera HUD**:
   * Live animated video canvas with CRT scanlines, 1080p HUD, and dynamic AI visitor bounding boxes.
   * Click **"Ring Chime"** to hear synthesized two-tone doorbell audio.
   * Switch between **Amazon Courier**, **Unverified Stranger**, **Neighbor Tom**, and **Clear Porch** in real-time.
2. **Alexa+ Ambient Voice Stage**:
   * Natural voice speech synthesis via Web Speech API (Alexa voice reads responses aloud).
   * Voice dictation using the **Microphone Button** (speak your queries directly!).
   * Animated pulsing Alexa orb and live audio equalizer waveforms.
3. **Smart Home Sensor Toggles**:
   * Toggle **Front Door Deadbolt** (`LOCKED` / `UNLOCKED`).
   * Toggle **Morning Metoprolol Dispenser** (`TAKEN` / `MISSED`).
   * Toggle **Kitchen Stove Gas Sensor** (`OFF` / `ON`).
4. **Caregiver SMS & MCP Stream Console**:
   * Visual smartphone preview displaying real-time Amazon SNS SMS pushes to Sarah Miller.
   * Real-time JSON-RPC 2.0 wire console showing live MCP tool requests and responses.

---

## Testing MCP Endpoints Programmatically

### Initialize MCP Protocol (Spec 2025-11-25)
```bash
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}'
```

### Discover Registered MCP Tools
```bash
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}'
```

### Execute Tool via MCP (`kinguard_get_door_snapshot`)
```bash
curl -X POST http://127.0.0.1:8080/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "kinguard_get_door_snapshot", "arguments": {}}}'
```

---

## License

This project is licensed under the [MIT License](LICENSE).  
Developed for the **Amazon Developer Hackathon (Build, Ship, Shape 2026)**.
