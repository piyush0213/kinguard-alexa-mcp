"""
KinGuard Alexa+ Agent Skill Runner (Enhanced with AWS Bedrock & SNS Integration).
Translates conversational queries from Alexa+ into MCP tool calls,
invokes Amazon Bedrock for clinical validation therapy steering,
and routes high-priority events through Amazon SNS.
"""

import os
import sys
import json
from typing import Dict, Any

# Ensure local imports work across package roots
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mcp_server.state_store import (
    get_visitor_state,
    set_visitor_response,
    get_medication_status,
    log_caregiver_alert,
    STATE
)
from aws_integration.bedrock_cognitive_engine import BedrockCognitiveEngine
from aws_integration.sns_dispatcher import AWSEscalationDispatcher

class KinGuardAlexaAgent:
    """
    Cognitive Guardrail Agent Skill running on Alexa+.
    Applies clinical validation therapy backed by Amazon Bedrock:
      - Validates emotion first (never invalidates or disputes memory directly).
      - Grounds factual answers with verifiable ambient telemetry via MCP tools.
      - Dispatches instant caregiver alerts over Amazon SNS.
    """

    def __init__(self):
        self.resident_name = STATE["resident"]["name"].split()[0]  # "Martha"
        self.bedrock_engine = BedrockCognitiveEngine()
        self.sns_dispatcher = AWSEscalationDispatcher()

    def handle_intent(self, intent_text: str) -> Dict[str, Any]:
        """
        Routes resident query to appropriate MCP cognitive tools and applies Bedrock steering.
        Prioritizes emotional distress / panic loops for caregiver safety.
        """
        text = intent_text.lower()

        # Priority 1: Emergency or High Anxiety Panic Loop
        if any(w in text for w in ["scared", "help", "panic", "emergency", "sarah", "daughter", "danger"]):
            alert_payload = {
                "resident_name": STATE["resident"]["name"],
                "severity": "HIGH",
                "reason": "Elevated panic / anxiety loop reported by resident",
                "context": f"Resident voice input: '{intent_text}'",
                "door_locked": STATE["door"]["door_locked"],
                "recipient": STATE["resident"]["primary_caregiver"]["name"]
            }
            dispatch_info = self.sns_dispatcher.dispatch_caregiver_alert(alert_payload)
            log_caregiver_alert("Resident requested assistance / elevated anxiety", "HIGH", intent_text)

            spoken_response = (
                f"I'm right here with you, {self.resident_name}. I have just sent an urgent note to Sarah "
                f"so she knows to check in. Take a slow, deep breath with me; your home is safe."
            )
            return {
                "mcp_tool_called": "kinguard_escalate_caregiver",
                "alexa_speech": spoken_response,
                "sns_dispatch": dispatch_info,
                "cognitive_intent": "EMERGENCY_ESCALATION",
                "aws_engine": "Amazon SNS & EventBridge"
            }

        # Scenario 2: Visitor response action (e.g. "Tell them to leave it on the porch")
        elif any(w in text for w in ["leave it", "porch", "drop it", "leave package"]):
            tts_to_visitor = "Please leave the parcel by the front door. Martha is resting inside. Thank you!"
            res = set_visitor_response("LEAVE_PACKAGE_ON_PORCH", tts_to_visitor)
            return {
                "mcp_tool_called": "kinguard_respond_door_visitor",
                "alexa_speech": f"I've spoken through the porch intercom and asked the courier to leave the package by the door. You don't need to get up, {self.resident_name}.",
                "intercom_delivered": tts_to_visitor,
                "cognitive_intent": "VISITOR_INTERCOM_DISPATCH",
                "aws_engine": "Amazon Bedrock (Claude 3.5)"
            }

        # Scenario 3: Visitor / Front Door / Doorbell anxiety
        elif any(w in text for w in ["door", "who is", "knocking", "bell", "outside", "stranger", "visitor"]):
            door_state = get_visitor_state()
            telemetry = {"door": door_state}
            steered_speech = self.bedrock_engine.steer_dialog(self.resident_name, intent_text, telemetry)

            return {
                "mcp_tool_called": "kinguard_get_door_snapshot",
                "alexa_speech": steered_speech,
                "suggested_actions": ["Ask them to leave on porch", "Come back later", "Unlock door"],
                "cognitive_intent": "DOOR_VERIFICATION",
                "aws_engine": "Amazon Bedrock (Claude 3.5)"
            }

        # Scenario 4: Medication memory verification (e.g. "Did I take my blood pressure pills?")
        elif any(w in text for w in ["medication", "pill", "medicine", "blood pressure", "metoprolol"]):
            meds = get_medication_status("Metoprolol")
            telemetry = {"medications": meds}
            steered_speech = self.bedrock_engine.steer_dialog(self.resident_name, intent_text, telemetry)

            return {
                "mcp_tool_called": "kinguard_verify_medication_state",
                "alexa_speech": steered_speech,
                "cognitive_intent": "MEDICATION_GROUNDING",
                "aws_engine": "Amazon Bedrock (Claude 3.5)"
            }

        # Scenario 5: General home safety anxiety (e.g. "Is the stove off?", "Are we safe?")
        elif any(w in text for w in ["stove", "safe", "lock", "house", "fire"]):
            telemetry = {"home_vitals": STATE["home_vitals"]}
            steered_speech = self.bedrock_engine.steer_dialog(self.resident_name, intent_text, telemetry)

            return {
                "mcp_tool_called": "kinguard_verify_home_safety",
                "alexa_speech": steered_speech,
                "cognitive_intent": "SAFETY_VALIDATION",
                "aws_engine": "Amazon Bedrock (Claude 3.5)"
            }

        # Default fallback
        else:
            telemetry = {"home_vitals": STATE["home_vitals"]}
            steered_speech = self.bedrock_engine.steer_dialog(self.resident_name, intent_text, telemetry)
            return {
                "mcp_tool_called": "kinguard_verify_home_safety",
                "alexa_speech": steered_speech,
                "cognitive_intent": "GENERAL_CARE_QUERY",
                "aws_engine": "Amazon Bedrock (Claude 3.5)"
            }

if __name__ == "__main__":
    agent = KinGuardAlexaAgent()
    print("Testing KinGuard with Bedrock integration...")
    r1 = agent.handle_intent("Who is at the front door?")
    print("Bedrock Steered Intent 1:", r1["alexa_speech"])
    r2 = agent.handle_intent("I am scared, someone is outside!")
    print("Bedrock Steered Intent 2:", r2["alexa_speech"])
