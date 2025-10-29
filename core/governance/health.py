
class HealthMonitor:
    def __init__(self):
        self.status = {}
    def report(self, service, status="READY", details=None):
        self.status[service] = {"status": status, "details": details}
    def get(self, service):
        return self.status.get(service, {"status":"UNKNOWN"})
