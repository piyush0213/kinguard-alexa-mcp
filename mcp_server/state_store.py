"""
KinGuard Simulation State & Data Store.
Maintains state for door camera, medication logs, and ambient home vitals.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List

# Simulated In-Memory State for Martha (Elderly Resident)
STATE: Dict[str, Any] = {
    "resident": {
        "name": "Martha Miller",
        "age": 78,
        "primary_caregiver": {
            "name": "Sarah Miller (Daughter)",
            "phone": "+1-555-019-2831",
            "relationship": "Daughter / Power of Attorney"
        },
        "care_notes": "Mild cognitive impairment (MCI). Susceptible to high anxiety during unexpected visits or routine disruption."
    },
    "door": {
        "has_active_visitor": True,
        "door_locked": True,
        "last_ring_timestamp": (datetime.now() - timedelta(minutes=1)).isoformat(),
        "active_visitor": {
            "visitor_id": "vis-8821",
            "detected_label": "Amazon Delivery Courier",
            "verification_status": "VERIFIED_SERVICE",
            "badge_details": "Amazon Prime Logistics - Route AP-9921",
            "carrying_item": "Medium cardboard parcel (#4029-AMZ)",
            "urgency_level": "LOW",
            "behavior": "Standing calmly at porch, holding parcel",
            "last_spoken_message": None
        }
    },
    "medications": [
        {
            "name": "Metoprolol Tartrate",
            "dosage": "25mg (Blood Pressure)",
            "scheduled_time": "09:00 AM",
            "status": "TAKEN",
            "verified_at": (datetime.now() - timedelta(minutes=45)).strftime("%I:%M %p"),
            "verification_sensor": "Smart Pill Dispenser Tray #1",
            "notes": "Taken with water 45 minutes ago. Next scheduled dose is at 08:00 PM."
        },
        {
            "name": "Donepezil",
            "dosage": "5mg (Cognitive Support)",
            "scheduled_time": "08:00 PM",
            "status": "PENDING",
            "verified_at": None,
            "verification_sensor": "Smart Pill Dispenser Tray #2",
            "notes": "Evening dose scheduled with dinner."
        }
    ],
    "home_vitals": {
        "stove_state": "OFF",
        "front_door_latch": "LOCKED",
        "ambient_temp_f": 71.5,
        "motion_status": "Active in Living Room (Normal)"
    },
    "caregiver_escalations": []
}

def get_visitor_state() -> Dict[str, Any]:
    return STATE["door"]

def trigger_doorbell_scenario(scenario: str) -> Dict[str, Any]:
    """Dynamically updates the front door visitor state for live interactive demonstrations."""
    now = datetime.now()
    if scenario == "amazon_courier":
        STATE["door"]["has_active_visitor"] = True
        STATE["door"]["last_ring_timestamp"] = now.isoformat()
        STATE["door"]["active_visitor"] = {
            "visitor_id": "vis-8821",
            "detected_label": "Amazon Delivery Courier",
            "verification_status": "VERIFIED_SERVICE",
            "badge_details": "Amazon Prime Logistics - Route AP-9921",
            "carrying_item": "Medium cardboard parcel (#4029-AMZ)",
            "urgency_level": "LOW",
            "behavior": "Standing calmly at porch, holding parcel",
            "last_spoken_message": None
        }
    elif scenario == "unverified_stranger":
        STATE["door"]["has_active_visitor"] = True
        STATE["door"]["last_ring_timestamp"] = now.isoformat()
        STATE["door"]["active_visitor"] = {
            "visitor_id": "vis-9904",
            "detected_label": "Unidentified Individual",
            "verification_status": "UNVERIFIED",
            "badge_details": "No identifiable uniform or credential detected",
            "carrying_item": "Clip-board / Flyers",
            "urgency_level": "MEDIUM",
            "behavior": "Pacing at front porch, looking at doorway",
            "last_spoken_message": None
        }
    elif scenario == "neighbor":
        STATE["door"]["has_active_visitor"] = True
        STATE["door"]["last_ring_timestamp"] = now.isoformat()
        STATE["door"]["active_visitor"] = {
            "visitor_id": "vis-1022",
            "detected_label": "Tom Higgins (Neighbor)",
            "verification_status": "VERIFIED_FAMILIAR",
            "badge_details": "Next-door resident (402 Elm St)",
            "carrying_item": "Garden basket / Casserole",
            "urgency_level": "LOW",
            "behavior": "Smiling, waving at Ring doorbell camera",
            "last_spoken_message": None
        }
    else:  # clear porch
        STATE["door"]["has_active_visitor"] = False
        STATE["door"]["active_visitor"] = {
            "visitor_id": None,
            "detected_label": "No Visitor",
            "verification_status": "PORCH_CLEAR",
            "badge_details": "Area Clear",
            "carrying_item": None,
            "urgency_level": "NONE",
            "behavior": "Porch empty",
            "last_spoken_message": None
        }
    return STATE["door"]

def toggle_medication_state(med_name: str, new_status: str) -> Dict[str, Any]:
    """Toggles medication dispenser state between TAKEN and MISSED / PENDING."""
    for m in STATE["medications"]:
        if med_name.lower() in m["name"].lower():
            m["status"] = new_status
            if new_status == "TAKEN":
                m["verified_at"] = datetime.now().strftime("%I:%M %p")
                m["notes"] = f"Dose verified by smart pill tray at {m['verified_at']}."
            else:
                m["verified_at"] = None
                m["notes"] = "Morning dose currently pending. Dispenser sensor has not registered tray opening."
            return m
    return {}

def toggle_stove_state(new_state: str) -> Dict[str, Any]:
    """Updates the kitchen stove vitals."""
    STATE["home_vitals"]["stove_state"] = new_state
    return STATE["home_vitals"]

def toggle_door_lock_state(is_locked: bool) -> Dict[str, Any]:
    """Updates the front door smart lock status."""
    STATE["door"]["door_locked"] = is_locked
    STATE["home_vitals"]["front_door_latch"] = "LOCKED" if is_locked else "UNLOCKED"
    return STATE["door"]

def set_visitor_response(action: str, spoken_tts: str) -> Dict[str, Any]:
    STATE["door"]["active_visitor"]["last_spoken_message"] = spoken_tts
    if action == "UNLOCK_DOOR":
        STATE["door"]["door_locked"] = False
        STATE["home_vitals"]["front_door_latch"] = "UNLOCKED"
    return {
        "action_taken": action,
        "spoken_to_visitor": spoken_tts,
        "timestamp": datetime.now().isoformat(),
        "door_locked": STATE["door"]["door_locked"]
    }

def get_medication_status(med_name: str = "") -> List[Dict[str, Any]]:
    if not med_name:
        return STATE["medications"]
    return [m for m in STATE["medications"] if med_name.lower() in m["name"].lower()]

def log_caregiver_alert(reason: str, severity: str, context: str) -> Dict[str, Any]:
    alert_record = {
        "alert_id": f"alert-{len(STATE['caregiver_escalations']) + 1}",
        "timestamp": datetime.now().isoformat(),
        "recipient": STATE["resident"]["primary_caregiver"],
        "reason": reason,
        "severity": severity,
        "context": context,
        "status": "SENT_VIA_SNS_SMS"
    }
    STATE["caregiver_escalations"].append(alert_record)
    return alert_record
