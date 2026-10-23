"""
KinGuard Integrated Server
Runs:
1. Model Context Protocol (MCP) Streamable HTTP & SSE server on /mcp and /mcp/sse
2. Alexa+ Cognitive Guardrail Agent API on /api/alexa/intent (steered by AWS Bedrock)
3. Web-based interactive Alexa+ & Ring Doorbell Simulator on /
"""

import os
import sys
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn

# Add root folder to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from mcp_server.state_store import (
    get_visitor_state,
    set_visitor_response,
    get_medication_status,
    log_caregiver_alert,
    STATE
)
from mcp_server.alexa_skill_agent import KinGuardAlexaAgent

app = FastAPI(
    title="KinGuard: Alexa+ MCP Server & Simulator",
    description="Cognitive Guardrail Agent Protocol for Alexa+, Ring & AWS",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

alexa_agent = KinGuardAlexaAgent()

# MCP Declarations
MCP_TOOLS = [
    {
        "name": "kinguard_get_door_snapshot",
        "description": "Inspects the front door camera / Ring feed. Returns visitor badge verification, package details, and visual assessment.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
    },
    {
        "name": "kinguard_respond_door_visitor",
        "description": "Dispatches a two-way intercom message to the front door visitor via Ring and optionally manages door latch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["LEAVE_PACKAGE_ON_PORCH", "TELL_VISITOR_COME_BACK_LATER", "UNLOCK_DOOR"]},
                "spoken_tts": {"type": "string"}
            },
            "required": ["action", "spoken_tts"],
            "additionalProperties": False
        }
    },
    {
        "name": "kinguard_verify_medication_state",
        "description": "Checks the smart medication tray dispenser state to ground memory and confirm if a dose was taken.",
        "inputSchema": {
            "type": "object",
            "properties": {"medication_name": {"type": "string"}},
            "additionalProperties": False
        }
    },
    {
        "name": "kinguard_verify_home_safety",
        "description": "Inspects ambient home vitals: stove state, door lock status, and living room motion.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}
    },
    {
        "name": "kinguard_escalate_caregiver",
        "description": "Sends an urgent notification to the family caregiver via Amazon SNS with incident context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
                "severity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]},
                "context": {"type": "string"}
            },
            "required": ["reason", "severity", "context"],
            "additionalProperties": False
        }
    }
]

def execute_mcp_tool(name: str, args: dict):
    if name == "kinguard_get_door_snapshot":
        return get_visitor_state()
    elif name == "kinguard_respond_door_visitor":
        return set_visitor_response(args.get("action", "LEAVE_PACKAGE_ON_PORCH"), args.get("spoken_tts", ""))
    elif name == "kinguard_verify_medication_state":
        return get_medication_status(args.get("medication_name", ""))
    elif name == "kinguard_verify_home_safety":
        return STATE["home_vitals"]
    elif name == "kinguard_escalate_caregiver":
        return log_caregiver_alert(args.get("reason", ""), args.get("severity", "MEDIUM"), args.get("context", ""))
    raise ValueError(f"Unknown tool {name}")

# MCP Protocol JSON-RPC Endpoint (Streamable HTTP spec 2025-11-25)
@app.post("/mcp")
async def handle_mcp_rpc(request: Request):
    body = await request.json()
    req_id = body.get("id", 1)
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-11-25",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "kinguard-mcp-server", "version": "1.0.0"}
            }
        }
    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": MCP_TOOLS}}
    elif method == "tools/call":
        try:
            output = execute_mcp_tool(params.get("name"), params.get("arguments", {}))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(output, indent=2)}], "isError": False}
            }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32603, "message": str(e)}}
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}

# MCP SSE Endpoint
@app.get("/mcp/sse")
async def mcp_sse(request: Request):
    async def sse_gen():
        yield "event: endpoint\ndata: /mcp\n\n"
    return StreamingResponse(sse_gen(), media_type="text/event-stream")

# Alexa+ Natural Language Agent Dialog API (Bedrock + MCP powered)
@app.post("/api/alexa/intent")
async def alexa_intent(request: Request):
    body = await request.json()
    query = body.get("query", "")
    response = alexa_agent.handle_intent(query)
    return response

# Interactive Simulator Controls & Telemetry APIs
@app.get("/api/simulator/telemetry")
async def get_telemetry():
    return {
        "status": "success",
        "state": STATE
    }

@app.post("/api/simulator/trigger_doorbell")
async def api_trigger_doorbell(request: Request):
    body = await request.json()
    scenario = body.get("scenario", "amazon_courier")
    from mcp_server.state_store import trigger_doorbell_scenario
    updated_door = trigger_doorbell_scenario(scenario)
    return {
        "status": "success",
        "scenario": scenario,
        "door": updated_door
    }

@app.post("/api/simulator/toggle_medication")
async def api_toggle_medication(request: Request):
    body = await request.json()
    med_name = body.get("med_name", "Metoprolol")
    status = body.get("status", "TAKEN")
    from mcp_server.state_store import toggle_medication_state
    med = toggle_medication_state(med_name, status)
    return {
        "status": "success",
        "medication": med
    }

@app.post("/api/simulator/toggle_stove")
async def api_toggle_stove(request: Request):
    body = await request.json()
    stove_state = body.get("state", "OFF")
    from mcp_server.state_store import toggle_stove_state
    vitals = toggle_stove_state(stove_state)
    return {
        "status": "success",
        "home_vitals": vitals
    }

@app.post("/api/simulator/toggle_lock")
async def api_toggle_lock(request: Request):
    body = await request.json()
    is_locked = body.get("locked", True)
    from mcp_server.state_store import toggle_door_lock_state
    door = toggle_door_lock_state(is_locked)
    return {
        "status": "success",
        "door": door
    }

@app.get("/api/simulator/alerts")
async def get_alerts():
    return {
        "status": "success",
        "alerts": STATE["caregiver_escalations"]
    }

# Mount Web Simulator UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    print("Starting KinGuard Integrated Server with AWS Bedrock on http://127.0.0.1:8080 ...")
    uvicorn.run("simulator_server:app", host="127.0.0.1", port=8080, reload=False)
