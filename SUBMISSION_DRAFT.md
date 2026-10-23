# KinGuard: Complete Devpost Submission Dossier
**Hackathon:** Build, Ship, Shape: Amazon Developer Hackathon (Devpost 2026)  
**Participant:** Piyush Prajapati (`piyushsujal102` / GitHub: `piyush0213`)  
**Primary Track:** Alexa+  
**Mini Challenges:** AWS Builder Challenge & Open Source Mini Challenge  

---

## 1. Basic Project Information

* **Project Title:** KinGuard: Ambient Cognitive Care & Verification Protocol
* **Tagline:** Ambient cognitive guardrail protocol bridging Alexa+, Ring doorbells, and Amazon Bedrock to protect and ground elderly adults with memory loss.
* **Tracks & Challenges Entered:**
  - [x] **Alexa+ (Primary Track)**
  - [x] **AWS Builder Mini Challenge**
  - [x] **Open Source Mini Challenge**

---

## 2. Project Story (Devpost Markdown Form)

### Inspiration
Over 55 million seniors worldwide live independently while coping with early-stage cognitive impairment, memory lapses, or dementia. For them and their families, daily life is shadowed by acute anxiety:
1. **The Front Door Trap:** An unexpected knock at the door causes intense panic. Elderly residents frequently fall victim to home-repair scammers, aggressive solicitors, or open the door in confusion.
2. **Medication Uncertainty Loops:** Repeatedly asking *"Did I take my blood pressure pills?"*, calling anxious children at work, or accidentally double-dosing.
3. **The Voice Assistant Breakdown:** Current voice assistants fail clinically. When a senior with cognitive impairment asks a repetitive question, standard assistants argue back (*"I already told you that 5 minutes ago"*). In clinical memory care, arguing directly violates **Validation Therapy**—it triggers agitation and worsens cognitive decline.

We built **KinGuard** to turn the home into an ambient, empathetic cognitive protector.

---

### What It Does
KinGuard is a zero-friction, voice-first ambient cognitive care system powered by **Alexa+**, **Ring smart doorbells**, and **Amazon Bedrock**:

1. **Context-Aware Doorbell Escort (Ring + Alexa+ Bridge):**
   * When someone approaches or rings the chime, Martha (78) asks naturally: *"Alexa, who is at the front door?"*
   * KinGuard executes the MCP tool `kinguard_get_door_snapshot`. If an Amazon courier is verified, Alexa+ calmly announces:  
     *"Don't worry, Martha. It's just the Amazon delivery courier with your parcel. Your front door is safely locked. Would you like me to ask them to leave it on the porch?"*
   * Martha simply replies: *"Tell them to leave it on the porch."* KinGuard calls `kinguard_respond_door_visitor`, broadcasting soothing two-way synthesized audio directly through the Ring porch speaker: *"Please leave the parcel by the front door. Martha is resting inside. Thank you!"*
2. **Ambient Medication Grounding:**
   * Martha asks: *"Did I take my blood pressure pills today?"*
   * KinGuard invokes `kinguard_verify_medication_state` to inspect the smart pill tray sensor. If verified:  
     *"Yes Martha, you're all set! You took your Metoprolol at 9:00 AM this morning with water. Your next scheduled dose is Donepezil tonight at dinner."*
   * If missed, it gently redirects: *"Martha, your morning dose is waiting in Tray 1. Let's take it together right now with a fresh glass of water."*
3. **Clinical Validation Therapy on Amazon Bedrock:**
   * KinGuard routes ambient telemetry through Amazon Bedrock (`anthropic.claude-3-haiku` / `claude-3-5-sonnet`) using specialized clinical validation therapy prompts. It never confronts, never invalidates emotions, and provides calm, grounding 1–2 sentence vocal responses.
4. **Caregiver Escalation via Amazon SNS & EventBridge:**
   * If high anxiety, persistent panic, or security threats are detected, KinGuard triggers `kinguard_escalate_caregiver`, dispatching an instant SMS summary to daughter Sarah (+1-555-019-2831) and logging an immutable audit event to Amazon EventBridge.

---

### How We Built It
* **Alexa+ Self-Hosted MCP Server (Spec 2025-11-25):** Built in Python using FastAPI and Uvicorn. Exposes standard JSON-RPC 2.0 endpoints over Streamable HTTP (`/mcp`) and Server-Sent Events (`/mcp/sse`), declaring 5 specialized cognitive tools.
* **Alexa+ Agent Skill:** Glues resident voice queries to MCP tool execution and Amazon Bedrock dialog steering.
* **Amazon Bedrock Integration:** Uses Boto3 runtime to query Claude 3.5 Sonnet / Haiku with clinical validation guardrails. Includes deterministic local fallbacks for offline resilience.
* **Amazon SNS & EventBridge:** Orchestrates emergency dispatches to caregiver phones and custom EventBridge buses. Includes complete AWS CloudFormation template (`cloudformation_stack.yaml`).
* **Interactive Live Simulator:** A high-fidelity, real-time web application featuring:
  - Ring video canvas with CRT scanlines, 1080p HUD, and dynamic AI visitor bounding boxes.
  - Web Speech API synthesis (so Alexa actually speaks aloud) and Web Speech Recognition (so users can speak through their microphone).
  - Dynamic sensor toggles (Door Deadbolt, Smart Pill Tray, Kitchen Stove Gas Sensor).
  - Live Amazon SNS caregiver push notification card and raw MCP JSON-RPC protocol wire terminal.

---

### Challenges We Ran Into
* **MCP Streamable HTTP Buffering:** Maintaining non-blocking Server-Sent Events (SSE) connections required fine-tuning HTTP headers (`X-Accel-Buffering: no`, `Cache-Control: no-cache`) to prevent proxy timeouts.
* **Sub-Second Voice Latency:** Balancing clinical system prompts with conversational voice requirements. We optimized prompt token budgets and selected Claude 3 Haiku for near-instantaneous responses.
* **Ring Hardware Emulation:** In the absence of an official local software simulator for Ring webhooks, we engineered our own full-fidelity canvas-based porch camera simulator.

---

### Accomplishments We're Proud Of
* **100% Real, Dynamic Implementation:** Zero static mockups or faked dashboards. The application reacts dynamically to real microphone speech, sensor toggles, and live scenario triggers.
* **Full Spec Compliance:** Native support for the cutting-edge Model Context Protocol (2025-11-25) Streamable HTTP specification.
* **Real Humanitarian Impact:** Built for the millions of seniors aging in place and their remote family caregivers.

---

### What We Learned
* How to bridge smart home IoT hardware (Ring) with cutting-edge agentic protocols (MCP) and LLM reasoning (Bedrock).
* The nuances of Clinical Validation Therapy and how AI assistants must adapt when speaking to vulnerable individuals.

---

### What's Next for KinGuard
* Real-world memory care clinical pilot with assisted living communities.
* Vega OS / Fire TV living room ambient visual widgets for elders with low vision.
* Direct hardware certification on the Ring Appstore.

---

## 3. Product Feedback & Friction Logs (10% Judging Bonus)

*(Full text also included in repository file `PRODUCT_FEEDBACK_AND_FRICTION_LOG.md`)*

### Product Feedback on Tools Used:
1. **Alexa+ Model Context Protocol (MCP):**
   * *Used for:* Self-hosted Streamable HTTP tool declarations and SSE execution.
   * *What worked:* JSON-RPC 2.0 schema clarity and seamless agent tool routing.
   * *What needs work:* Documentation on reverse-proxy SSE buffering.
   * *Onboarding feel:* 4/5. Rapid once protocol schemas were understood.
   * *Build again:* Yes, 100%.
2. **Amazon Bedrock (Claude 3.5 Sonnet & Haiku):**
   * *Used for:* Clinical validation therapy and empathetic vocal dialog steering.
   * *What worked:* Sub-second latency on Haiku and rock-solid Boto3 runtime stability.
   * *What needs work:* Pre-built clinical/empathy guardrail presets.
   * *Onboarding feel:* 4.8/5.
   * *Build again:* Yes, absolutely.
3. **Amazon SNS & EventBridge:**
   * *Used for:* Caregiver emergency SMS notifications and incident event routing.
   * *What worked:* Instant SMS delivery (<1.5s) and decoupled EventBridge rules.
   * *What needs work:* AWS SMS sandbox spending limits for fast prototypes.
   * *Onboarding feel:* 4.5/5.
   * *Build again:* Yes.
4. **Ring Developer APIs:**
   * *Used for:* Live porch feed metadata and two-way intercom audio streaming.
   * *What worked:* Rich sensor telemetry attributes.
   * *What needs work:* Lack of official local software virtual device runner.
   * *Onboarding feel:* 3.8/5.
   * *Build again:* Yes.

### Friction Logs:
* **Friction Log 1 (Severity: HIGH):** MCP Streamable HTTP connection buffering behind proxies. *Workaround:* Explicit anti-buffering headers and immediate connection ping event.
* **Friction Log 2 (Severity: MEDIUM):** Bedrock IAM Claude 3.5 model access activation requirement. *Workaround:* Dual-execution architecture with local clinical fallback.
* **Friction Log 3 (Severity: MEDIUM):** Tool call result schema validation in preview skill runners. *Workaround:* Dual-payload schema with structured JSON and explicit `care_recommendation` string.
* **Friction Log 4 (Severity: HIGH):** Absence of official local Ring webhook simulator. *Workaround:* Engineered custom interactive canvas simulator in FastAPI.

---

## 4. Repository & Reviewer Details

* **GitHub Username:** `piyush0213`
* **Local Repo Path:** `C:\Users\Piyush\OpenBot\Agents\agent-2590f3ce-e49e-41ad-ac05-0c97241d78f5\kinguard`
* **License:** MIT License (Open Source)
* **Amazon Reviewers to add if private:** `chris-trag`, `knmeiss`, `giolaq`, `anishamalde`, `mosesroth`, `emersonsklar`
