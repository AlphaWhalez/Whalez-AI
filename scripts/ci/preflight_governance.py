#!/usr/bin/env python
import json, time
from core.governance import PolicyEngine, PolicyViolation, AuditLogger, HealthMonitor, ServiceDeployer

def main():
    audit = AuditLogger()
    health = HealthMonitor()
    deployer = ServiceDeployer(audit=audit, health=health)
    engine = PolicyEngine(audit=audit)

    # register a basic policy: service must declare a port and name
    @engine.policy("service_has_minimum_fields")
    def _p(service):
        required = {"name","port"}
        missing = required - set(service)
        if missing:
            raise PolicyViolation(f"missing fields: {sorted(missing)}")

    # dummy desired service
    svc = {"name":"demo-api","port":8080,"runtime":"local"}
    engine.enforce(svc)

    # simulate health + deploy
    health.report("demo-api", status="READY")
    deployer.deploy(svc)

    print(json.dumps({"ok": True, "ts": time.time()}))

if __name__ == "__main__":
    main()
