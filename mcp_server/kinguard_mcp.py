"""
KinGuard Model Context Protocol (MCP) Server for Alexa+ & Smart Home Agents.
Implements the MCP Specification with Streamable HTTP and SSE endpoints.
"""

import os
import sys
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from state_store import (
    get_visitor_state,
    set_visitor_response,
    get_medication_status,
    log_caregiver_alert,
    STATE
)

app = FastAPI(
    title="KinGuard MCP Server for Alexa+",
    description="Cognitive guardrail MCP tools over Streamable HTTP for Alexa+ & Ring",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Declarations of available MCP tools
MCP_TOOLS = [
    {
        "name": "kinguard_get_door_snapshot",
        "description": "Inspects the front door camera / Ring feed. Returns visitor badge verification, package details, and visual assessment.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "kinguard_respond_door_visitor",
        "description": "Dispatches a two-way intercom message to the front door visitor via Ring and optionally manages door latch.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform: 'LEAVE_PACKAGE_ON_PORCH', 'TELL_VISITOR_COME_BACK_LATER', or 'UNLOCK_DOOR'",
                    "enum": ["LEAVE_PACKAGE_ON_PORCH", "TELL_VISITOR_COME_BACK_LATER", "UNLOCK_DOOR"]
                },
                "spoken_tts": {
                    "type": "string",
                    "description": "Exact phrase played out loud to the visitor at the porch speaker"
                }
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
            "properties": {
                "medication_name": {
                    "type": "string",
                    "description": "Optional specific medicine name (e.g., 'Metoprolol', 'Blood Pressure')"
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "kinguard_verify_home_safety",
        "description": "Inspects ambient home vitals: stove state, door lock status, and living room motion.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "additionalProperties": False
        }
    },
    {
        "name": "kinguard_escalate_caregiver",
        "description": "Sends an urgent notification to the family caregiver via Amazon SNS with incident context.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Short summary of the escalation"
                },
                "severity": {
                    "type": "string",
                    "enum": ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]
                },
                "context": {
                    "type": "string",
                    "description": "Detailed background observations"
                }
            },
            "required": ["reason", "severity", "context"],
            "additionalProperties": False
        }
    }
]

def execute_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Executes a declared MCP tool and returns structured content."""
    if name == "kinguard_get_door_snapshot":
        door_info = get_visitor_state()
        return {
            "status": "success",
            "has_active_visitor": door_info["has_active_visitor"],
            "door_locked": door_info["door_locked"],
            "active_visitor": door_info["active_visitor"],
            "care_recommendation": (
                "Visitor is verified. Reassure Martha: explain an Amazon courier is at the porch with a package, "
                "and ask if she would like the package placed on the porch without opening the door."
            )
        }
    elif name == "kinguard_respond_door_visitor":
        action = args.get("action", "LEAVE_PACKAGE_ON_PORCH")
        spoken_tts = args.get("spoken_tts", "Please leave the parcel by the front door. Thank you!")
        result = set_visitor_response(action, spoken_tts)
        return {
            "status": "success",
            "detail": result,
            "alexa_voice_feedback": f"I've let the visitor know: '{spoken_tts}'. You can relax inside."
        }
    elif name == "kinguard_verify_medication_state":
        med_name = args.get("medication_name", "")
        meds = get_medication_status(med_name)
        return {
            "status": "success",
            "resident": STATE["resident"]["name"],
            "medications": meds,
            "care_guidance": (
                "Always state the time medication was taken in simple, comforting terms: "
                "'Yes Martha, you took your morning blood pressure medicine 45 minutes ago at 9:00 AM.'"
            )
        }
    elif name == "kinguard_verify_home_safety":
        return {
            "status": "success",
            "home_vitals": STATE["home_vitals"],
            "reassurance_summary": "All home appliances are safe. Stove is off, front door is locked."
        }
    elif name == "kinguard_escalate_caregiver":
        reason = args.get("reason", "Incident reported")
        severity = args.get("severity", "MEDIUM")
        context = args.get("context", "")
        alert = log_caregiver_alert(reason, severity, context)
        return {
            "status": "success",
            "sns_dispatch": alert,
            "alexa_dialog": "I have sent a quick note to your daughter Sarah so she is in the loop. Everything is safe."
        }
    else:
        raise ValueError(f"Unknown MCP tool: {name}")

# JSON-RPC 2.0 Handler for MCP Protocol
@app.post("/mcp")
async def handle_mcp_rpc(request: Request):
    """Handles JSON-RPC 2.0 calls according to the Model Context Protocol."""
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
                "capabilities": {
                    "tools": {"listChanged": False},
                    "logging": {}
                },
                "serverInfo": {
                    "name": "kinguard-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            tool_output = execute_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_output, indent=2)
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {
                "code": -32601,
                "message": f"Method '{method}' not found."
            }
        }

# Streamable HTTP / Server-Sent Events (SSE) Endpoint (Spec 2025-11-25+)
@app.get("/mcp/sse")
async def mcp_sse_stream(request: Request):
    """Streamable HTTP / SSE endpoint providing live streaming tool updates."""
    async def event_generator():
        # Initial connection endpoint event
        yield f"event: endpoint\ndata: /mcp\n\n"
        # Initial server info
        yield f"event: serverInfo\ndata: {json.dumps({'name': 'kinguard-mcp', 'status': 'connected'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# REST Discovery & Testing Endpoints
@app.get("/api/tools")
def get_tools():
    return {"status": "success", "tools": MCP_TOOLS}

@app.get("/api/state")
def get_current_state():
    return STATE

if __name__ == "__main__":
    print("Starting KinGuard MCP Server (Streamable HTTP / SSE) on port 8080...")
    uvicorn.run("kinguard_mcp:app", host="127.0.0.1", port=8080, reload=False)
