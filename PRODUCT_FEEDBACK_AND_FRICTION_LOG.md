# KinGuard: Amazon Developer Product Feedback & Friction Logs
*Submission for "Build, Ship, Shape: Amazon Developer Hackathon" (Devpost 2026)*
*Primary Track: Alexa+ | Mini-Challenges: AWS Builder & Open Source*

---

## 1. Developer Product Feedback (Required Submission Field)

### A. Alexa+ Model Context Protocol (MCP) — Streamable HTTP & SSE (Spec 2025-11-25+)
* **What we used it for:**
  We implemented a self-hosted Model Context Protocol server exposing clinical cognitive tools (`kinguard_get_door_snapshot`, `kinguard_respond_door_visitor`, `kinguard_verify_medication_state`, `kinguard_verify_home_safety`, `kinguard_escalate_caregiver`) communicating over Streamable HTTP (`POST /mcp`) and Server-Sent Events (`GET /mcp/sse`).
* **What worked well:**
  The standardization of JSON-RPC 2.0 schemas for tool discovery (`tools/list`) and invocation (`tools/call`) allows Alexa+ agent workflows to dynamically ground their reasoning without requiring hard-coded intent slots. The streamable SSE protocol allows long-running camera inspections to deliver progressive chunks back to Alexa+.
* **What needs work:**
  The MCP specification (2025-11-25) lacks clear reference implementations for bidirectional SSE streaming over reverse proxies (e.g. Nginx / AWS CloudFront). Initial handshake handoffs require explicit headers (`X-Accel-Buffering: no`, `Cache-Control: no-cache`), which are poorly documented in standard Alexa+ onboarding guides.
* **Onboarding feel:**
  Rating: **4/5**. For developers already familiar with agentic tool calling and FastAPI/Uvicorn, setup was relatively rapid. However, developers new to SSE streaming may find the lack of turnkey Python MCP client adapters frustrating.
* **Would we build with it again:**
  **Yes, absolutely.** MCP is the undeniable future of voice assistant tool integrations, far surpassing legacy Alexa Skills Kit (ASK) intent-schema limitations.

---

### B. Amazon Bedrock (Anthropic Claude 3.5 Sonnet & Haiku Runtime)
* **What we used it for:**
  Enforcing clinical cognitive validation therapy and empathetic dialog steering. Bedrock ingests raw IoT telemetry from Ring and smart medication trays and synthesizes 1–2 sentence soothing vocal responses that validate the resident's emotions without disputing their memory.
* **What worked well:**
  Sub-second inference latency on `anthropic.claude-3-haiku` allows conversational Alexa+ dialog to feel immediate and natural. The Boto3 `invoke_model` API is rock-solid and requires zero model maintenance or cold-start overhead.
* **What needs work:**
  Bedrock Guardrails currently focus heavily on PII masking and toxicity filtering, but lack native pre-built templates for healthcare or cognitive validation therapy (e.g. preventing the assistant from arguing with dementia patients). We had to hand-craft clinical system prompts.
* **Onboarding feel:**
  Rating: **4.8/5**. One-click model access in AWS Console us-east-1 and standard IAM policies made Bedrock the smoothest part of the stack.
* **Would we build with it again:**
  **Yes, 100%.** Bedrock is our preferred foundation for all mission-critical ambient AI workloads.

---

### C. Amazon SNS & Amazon EventBridge
* **What we used it for:**
  Routing critical caregiver escalations, panic incidents, and door safety alerts directly to family caregivers (e.g., Sarah Miller) via SMS, while publishing immutable audit trails to a custom EventBridge bus.
* **What worked well:**
  Instantaneous SMS delivery (< 1.5 seconds) to verified phone numbers without needing third-party telephony providers like Twilio. EventBridge rule matching on `detail.severity = ["HIGH", "EMERGENCY"]` allowed seamless decoupling of notification routing.
* **What needs work:**
  AWS SMS Sandbox spending limits ($1.00/month by default) require manual service quota increase tickets for production rollout, which can surprise hackathon builders.
* **Onboarding feel:**
  Rating: **4.5/5**. Mature, predictable AWS primitives.
* **Would we build with it again:**
  **Yes.** Essential for caretaking workflows.

---

### D. Ring Developer APIs & Simulator
* **What we used it for:**
  Live front porch video verification, courier badge identification, and two-way porch intercom audio dispatching via `kinguard_respond_door_visitor`.
* **What worked well:**
  Rich metadata attributes (visitor presence, motion detection, camera snapshot triggers) translate effortlessly into MCP tool arguments.
* **What needs work:**
  Lack of an official local software mock/simulator package for developers without physical Ring hardware. We built our own high-fidelity canvas simulator to bridge this gap.
* **Onboarding feel:**
  Rating: **3.8/5**. Physical hardware dependency in the official ecosystem creates friction for pure software developers.
* **Would we build with it again:**
  **Yes.** The combination of Ring cameras and Alexa+ voice agents creates unmatched peace of mind for families.

---

## 2. Friction Log Entries (Judging Bonus)

### Friction Log #1: MCP Streamable HTTP Connection Buffering & Timeout
* **Task Attempted:** Connecting an Alexa+ simulated agent to the self-hosted MCP server over Server-Sent Events (`/mcp/sse`).
* **Steps Taken:** Implemented standard FastAPI `StreamingResponse` yielding SSE chunks (`event: endpoint\ndata: /mcp\n\n`).
* **Expected vs. Actual:**
  * *Expected:* Client establishes immediate connection and receives streaming tool definitions.
  * *Actual:* Connection hung indefinitely behind proxies due to chunk buffering; clients timed out after 30 seconds.
* **Severity Rating:** **HIGH**
* **Workaround Used:** Added explicit anti-buffering headers (`X-Accel-Buffering: no`, `Cache-Control: no-cache, no-transform`, `Connection: keep-alive`) and flushed an initial empty keep-alive ping immediately upon connection.
* **Actionable Suggestion for Amazon:** Include standard middleware recipes in the official Alexa+ MCP SDK samples that automatically inject streaming SSE headers.

---

### Friction Log #2: Bedrock IAM Permission Scoping for Claude 3.5 Models
* **Task Attempted:** Invoking `anthropic.claude-3-5-sonnet-20240620-v1:0` via Boto3 in an automated pipeline.
* **Steps Taken:** Assigned standard `AmazonBedrockFullAccess` managed policy to the IAM execution role.
* **Expected vs. Actual:**
  * *Expected:* Boto3 invokes the Claude 3.5 model successfully.
  * *Actual:* Returned `AccessDeniedException` because Anthropic Claude models require explicit EULA activation in the AWS Bedrock Model Access console before programmatic IAM permissions take effect.
* **Severity Rating:** **MEDIUM**
* **Workaround Used:** Created a dual-execution fallback architecture: if AWS credentials or model access are unactivated, KinGuard gracefully transitions to deterministic local clinical steering so developers never encounter a hard crash.
* **Actionable Suggestion for Amazon:** Provide a programmatic AWS CLI or Boto3 command (`bedrock.request_model_access`) to accept foundation model terms programmatically.

---

### Friction Log #3: Tool Call Result Schema Validation in Alexa+ Agent Skill
* **Task Attempted:** Returning structured JSON-RPC responses containing nested sensor vitals from `kinguard_verify_home_safety`.
* **Steps Taken:** Returned dictionary containing integer temperatures and boolean flags inside the `content[0].text` payload.
* **Expected vs. Actual:**
  * *Expected:* Alexa+ agent parses the nested JSON string without error.
  * *Actual:* Certain Alexa+ Preview skill runners expected flat key-value pairs or stringified descriptions, causing silent agent fallbacks.
* **Severity Rating:** **MEDIUM**
* **Workaround Used:** Formatted MCP tool returns with both a structured dictionary and an explicit, human-readable `care_recommendation` summary string to guarantee infallible agent parsing.
* **Actionable Suggestion for Amazon:** Publish a canonical JSON schema validator tool for Alexa+ MCP tool return payloads.

---

### Friction Log #4: Absence of Official Local Ring Webhook Simulator
* **Task Attempted:** End-to-end testing of live doorbell chime events and visitor arrival webhooks without active Ring hardware.
* **Steps Taken:** Searched Ring Developer portal and npm/pip repositories for an official Ring virtual device runner.
* **Expected vs. Actual:**
  * *Expected:* A lightweight CLI or Docker image simulating Ring camera webhooks.
  * *Actual:* None available; documentation assumes physical hardware paired to an active Ring Protect subscription.
* **Severity Rating:** **HIGH**
* **Workaround Used:** Architected our own interactive Ring Porch Camera Simulator in `simulator_server.py` and `static/index.html` with real-time video canvas, two-way intercom audio state, and scenario triggers.
* **Actionable Suggestion for Amazon:** Release an open-source Ring Device Simulator (similar to the Alexa Skills Kit Simulator) to accelerate third-party developer adoption.

---

## 3. Strategic Feature Requests for Amazon Developer Teams

1. **Native Clinical / Empathy Guardrail Presets in Amazon Bedrock**
   * *Urgency:* **Important**
   * *Why it matters:* Millions of developers are building healthcare, eldercare, and customer crisis agents. Having pre-certified validation therapy guardrails in Bedrock prevents accidental confrontation and hallucinated disputes.
2. **One-Click Alexa+ MCP Hosting on AWS Lambda / App Runner**
   * *Urgency:* **Critical**
   * *Why it matters:* Hosting MCP servers currently requires managing VPS or ECS containers with open ports for SSE. A native AWS Lambda Streamable HTTP adapter for Alexa+ would enable zero-maintenance, serverless MCP deployments.
3. **Unified Ring & Alexa+ Two-Way Audio Streaming Bridge**
   * *Urgency:* **Nice-to-Have**
   * *Why it matters:* Allowing Alexa+ agents to directly stream synthesized TTS audio into Ring porch speakers with sub-200ms latency without intermediary polling.
