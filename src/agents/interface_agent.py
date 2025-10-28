class InterfaceAgent:
    def __init__(self):
        self.status = "idle"

    def current_task(self):
        return "Idle — waiting for request"

    def heartbeat(self):
        return {"status": self.status}
