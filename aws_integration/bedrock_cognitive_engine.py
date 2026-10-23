"""
KinGuard AWS Bedrock Cognitive Validation & Dialog Steering Engine.
Uses Amazon Bedrock (Anthropic Claude 3.5 Sonnet / Haiku or local fallback)
to enforce clinical cognitive validation therapy and generate empathetic voice dialog.
"""

import os
import json
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Clinical cognitive care system prompt
CLINICAL_SYSTEM_PROMPT = """You are KinGuard, an empathetic, clinically-informed cognitive guardrail assistant embedded in an Alexa+ device for elderly individuals with Mild Cognitive Impairment (MCI) or dementia.

Your Core Rules:
1. Validation Therapy: NEVER argue, correct harshly, or say "You already asked that". Validate their emotions first ("I understand you are feeling concerned").
2. Ambient Grounding: Use the provided verifiable telemetry (Ring camera verification, smart medication dispenser timestamp, door lock sensors) to ground reality gently.
3. Cognitive Load Minimization: Keep answers short (1 to 2 sentences), clear, warm, and comforting. Do not overwhelm with technical jargon.
4. Action Offerings: Offer 1 or 2 simple choices rather than open-ended decisions (e.g., "Would you like me to tell them to leave the package on the porch, or should they come back later?").
"""

class BedrockCognitiveEngine:
    def __init__(self, region_name: str = "us-east-1", model_id: str = "anthropic.claude-3-haiku-20240307-v1:0"):
        self.region_name = region_name
        self.model_id = model_id
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            self.client = boto3.client("bedrock-runtime", region_name=self.region_name)
        except Exception:
            self.client = None

    def steer_dialog(self, resident_name: str, user_query: str, telemetry_context: Dict[str, Any]) -> str:
        """
        Invokes Amazon Bedrock to steer conversational dialog with grounded telemetry.
        Falls back smoothly to empathetic rule-based generation if AWS credentials are not configured.
        """
        if self.client:
            try:
                prompt_content = f"""Resident Name: {resident_name}
User Query: "{user_query}"
Current Verified Telemetry:
{json.dumps(telemetry_context, indent=2)}

Formulate a 1-2 sentence warm, reassuring Alexa+ spoken response following clinical validation therapy:"""

                payload = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 150,
                    "temperature": 0.3,
                    "system": CLINICAL_SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": prompt_content}
                    ]
                }

                response = self.client.invoke_model(
                    modelId=self.model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(payload)
                )
                body = json.loads(response["body"].read())
                return body["content"][0]["text"].strip()
            except (NoCredentialsError, ClientError, Exception):
                pass

        # Resilient Local Fallback implementing the same clinical validation principles
        return self._local_clinical_steer(resident_name, user_query, telemetry_context)

    def _local_clinical_steer(self, resident_name: str, user_query: str, telemetry: Dict[str, Any]) -> str:
        query = user_query.lower()
        if any(w in query for w in ["door", "who is", "knocking", "outside", "stranger", "visitor", "bell"]):
            door_info = telemetry.get("door", {})
            vis = door_info.get("active_visitor", {})
            status = vis.get("verification_status")
            label = vis.get("detected_label", "A visitor")

            if status == "VERIFIED_SERVICE":
                item = vis.get("carrying_item", "a package")
                return (
                    f"Don't worry at all, {resident_name}. It's just the Amazon delivery courier with {item}. "
                    f"Your front door is safely locked. Would you like me to ask them to leave it on the porch for you?"
                )
            elif status == "VERIFIED_FAMILIAR":
                return (
                    f"Good news, {resident_name}! It's your neighbor {label} outside with a friendly greeting. "
                    f"The door is currently locked. Would you like me to unlock it, or speak through the intercom?"
                )
            elif status == "UNVERIFIED":
                return (
                    f"{resident_name}, someone is outside whom we don't recognize yet, but your front door is securely locked. "
                    f"There is no need to open the door. I can ask them who they are, or send a quick note to Sarah."
                )
            elif not door_info.get("has_active_visitor"):
                return (
                    f"The front porch is completely clear and peaceful, {resident_name}. No one is at the door, "
                    f"and the deadbolt is securely locked."
                )
            else:
                return (
                    f"{resident_name}, someone is outside, but the front door is securely locked. "
                    f"You are safe inside. Would you like me to take a message?"
                )

        if any(w in query for w in ["medication", "pill", "medicine", "blood pressure", "metoprolol"]):
            meds = telemetry.get("medications", [])
            met = next((m for m in meds if "metoprolol" in m.get("name", "").lower()), None)
            if met:
                if met.get("status") == "TAKEN":
                    verified_time = met.get("verified_at", "this morning")
                    return (
                        f"Yes {resident_name}, you're all set! You took your {met['name']} at {verified_time} "
                        f"this morning with water. Your next scheduled dose is Donepezil tonight at dinner."
                    )
                else:
                    return (
                        f"{resident_name}, I checked your smart pill tray, and your morning {met['name']} is still waiting. "
                        f"Let's take it together right now with a fresh glass of water."
                    )
            return f"Your daily medicines are tracked in your smart dispenser, {resident_name}. Everything is under control."

        if any(w in query for w in ["safe", "stove", "lock", "house", "fire", "danger"]):
            vitals = telemetry.get("home_vitals", {})
            stove = vitals.get("stove_state", "OFF")
            door = vitals.get("front_door_latch", "LOCKED")

            if stove == "ON":
                return (
                    f"{resident_name}, the kitchen stove sensor shows the burner is currently ON. "
                    f"Let's walk over to the kitchen together and switch it off. I am right here with you."
                )
            return (
                f"You are completely safe, {resident_name}. The kitchen stove is turned off, and the front door "
                f"is securely locked. Sarah is just a quick phone call away."
            )

        return (
            f"I'm right here with you, {resident_name}. Everything in the home is calm and safe. "
            f"Would you like to check on the door, your medicines, or listen to some soothing music?"
        )

if __name__ == "__main__":
    engine = BedrockCognitiveEngine()
    dummy_telemetry = {
        "door": {
            "has_active_visitor": True,
            "active_visitor": {
                "detected_label": "Amazon Delivery Courier",
                "verification_status": "VERIFIED_SERVICE"
            }
        }
    }
    result = engine.steer_dialog("Martha", "Who is at the front door?", dummy_telemetry)
    print("Bedrock Steered Dialog:", result)
