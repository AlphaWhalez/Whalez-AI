
from core.governance import PolicyEngine, PolicyViolation, AuditLogger, HealthMonitor, ServiceDeployer

class Orchestrator:
    def __init__(self):
        self.audit = AuditLogger()
        self.health = HealthMonitor()
        self.engine = PolicyEngine(audit=self.audit)
        self.deployer = ServiceDeployer(audit=self.audit, health=self.health)

        @self.engine.policy("require_name_and_port")
        def _p(svc):
            if not svc.get("name") or not svc.get("port"):
                raise PolicyViolation("service requires 'name' and 'port'")

    def reconcile(self, desired_services):
        results = []
        for svc in desired_services:
            self.engine.enforce(svc)
            self.deployer.deploy(svc)
            results.append({"name": svc["name"], "status": "DEPLOYED"})
        return {"results": results, "audit": self.audit.list()}
