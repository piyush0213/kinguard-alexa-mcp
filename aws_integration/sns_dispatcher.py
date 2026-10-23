"""
KinGuard AWS SNS & EventBridge Dispatcher.
Manages automated alert propagation for family caregivers and home security triggers.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

class AWSEscalationDispatcher:
    def __init__(self, region_name: str = "us-east-1"):
        self.region_name = region_name
        self.sns_client = None
        self.events_client = None
        self.sns_topic_arn = os.environ.get("SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:123456789012:kinguard-caregiver-alerts")
        self._init_clients()

    def _init_clients(self):
        try:
            self.sns_client = boto3.client("sns", region_name=self.region_name)
            self.events_client = boto3.client("events", region_name=self.region_name)
        except Exception:
            pass

    def dispatch_caregiver_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches SMS/Push alert via Amazon SNS and emits audit event to Amazon EventBridge.
        """
        message_body = (
            f"[KinGuard Alert: {alert_data.get('severity', 'HIGH')}]\n"
            f"Resident: {alert_data.get('resident_name', 'Martha')}\n"
            f"Reason: {alert_data.get('reason')}\n"
            f"Details: {alert_data.get('context')}\n"
            f"Door Status: {alert_data.get('door_locked', True) and 'Locked' or 'Unlocked'}\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        aws_dispatched = False
        message_id = f"sim-{datetime.now().timestamp()}"

        if self.sns_client:
            try:
                res = self.sns_client.publish(
                    TopicArn=self.sns_topic_arn,
                    Message=message_body,
                    Subject=f"KinGuard Care Alert for {alert_data.get('resident_name', 'Martha')}"
                )
                message_id = res.get("MessageId", message_id)
                aws_dispatched = True
            except Exception:
                pass

        if self.events_client:
            try:
                self.events_client.put_events(
                    Entries=[{
                        "Source": "kinguard.cognitive.agent",
                        "DetailType": "CaregiverEscalationEvent",
                        "Detail": json.dumps(alert_data),
                        "EventBusName": "default"
                    }]
                )
            except Exception:
                pass

        return {
            "status": "DISPATCHED",
            "aws_sns_dispatched": aws_dispatched,
            "message_id": message_id,
            "recipient": alert_data.get("recipient", "Sarah Miller (+1-555-019-2831)"),
            "formatted_message": message_body
        }

if __name__ == "__main__":
    dispatcher = AWSEscalationDispatcher()
    sample = {
        "resident_name": "Martha Miller",
        "severity": "HIGH",
        "reason": "Elevated visitor anxiety",
        "context": "Visitor rang porch doorbell twice. Resident expressed uncertainty.",
        "door_locked": True
    }
    result = dispatcher.dispatch_caregiver_alert(sample)
    print("Alert Dispatch Result:", json.dumps(result, indent=2))
