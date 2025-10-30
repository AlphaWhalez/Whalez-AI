
import asyncio

from core.governance import PolicyEngine, PolicyViolation, AuditLogger, HealthMonitor, ServiceDeployer

try:
    from core.intent import get_engine
except Exception:  # pragma: no cover
    get_engine = None  # type: ignore

try:
    from core.telemetry.streamer import log_event as _emit
except Exception:  # pragma: no cover
    async def _emit(kind, data):  # type: ignore
        return None


def _emit_async(kind: str, data):
    """Best-effort async emitter that never raises."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            return
        if not loop.is_running():
            return
    try:
        loop.create_task(_emit(kind, data))
    except Exception:
        return

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
            intent_name = svc.get("name", "service")
            _emit_async("intent.enqueue", {"name": intent_name, "meta": svc})
            _emit_async("intent.start", {"name": intent_name})
            try:
                self.engine.enforce(svc)
                self.deployer.deploy(svc)
            except Exception as exc:
                _emit_async("intent.fail", {"name": intent_name, "error": str(exc)})
                raise
            else:
                _emit_async("intent.done", {"name": intent_name, "status": "ok"})
            results.append({"name": svc["name"], "status": "DEPLOYED"})
        return {"results": results, "audit": self.audit.list()}


async def request_reconcile(target: str = "dummy-service") -> dict:
    """Enqueue a reconcile intent via the global engine and return metadata."""

    if not get_engine:
        return {"ok": False, "error": "intent engine unavailable"}
    engine = get_engine()
    intent = await engine.reconcile(target=target)
    return {"ok": True, "intent_id": intent.id, "name": intent.name, "target": target}
