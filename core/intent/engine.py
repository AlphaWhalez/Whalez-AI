import json
import time

from core.security.vault import get_secret
from core.governance.policy_engine import PolicyViolation

class IntentEngine:
    def __init__(self):
        self.queue = []
        self.status = "idle"

    def load_intent(self, intent):
        """Receive new intent from governance console."""
        self.queue.append(intent)
        print(f"[IntentEngine] Intent received: {intent['name']}")

    def evaluate(self, intent):
        """Check with governance and security layers."""
        if intent.get("policy") == "restricted":
            raise PolicyViolation("Intent not authorized by governance.")
        return True

    def execute(self, intent):
        """Execute validated intents."""
        try:
            if self.evaluate(intent):
                self.status = "executing"
                session_token = get_secret("intent_engine/session_token", default="dev-session")
                audit_payload = json.dumps({"intent": intent["name"], "token": session_token})
                print(f"[IntentEngine] Audit payload: {audit_payload}")
                print(f"[IntentEngine] Executing: {intent['name']}")
                time.sleep(1)
                print(f"[IntentEngine] ✅ Completed intent: {intent['name']}")
                self.status = "idle"
        except PolicyViolation as e:
            print(f"[IntentEngine] ❌ PolicyViolation: {str(e)}")

# Bootstrap
if __name__ == "__main__":
    engine = IntentEngine()
    sample_intent = {"name": "initialize_self_heal", "policy": "open"}
    engine.load_intent(sample_intent)
    engine.execute(sample_intent)
