
import time, json
class AuditLogger:
    def __init__(self):
        self.events = []
    def log(self, event, **fields):
        rec = {"ts": time.time(), "event": event, **fields}
        self.events.append(rec)
        print(json.dumps(rec))
    def list(self):
        return list(self.events)
