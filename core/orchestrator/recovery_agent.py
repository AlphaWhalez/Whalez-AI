# self-heal controller: probe -> decide -> reconcile(deploy/rollback)
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List
import os

from core.orchestrator.state_store import StateStore
from core.orchestrator.health import check_cmd

# NOTE: these shell hooks are simple and safe: you already have scripts/linux/* and windows/*.
LINUX_RESTART = os.environ.get("SERVICE_RESTART_CMD", "scripts/linux/start_orchestrator.sh")
WINDOWS_RESTART = os.environ.get("SERVICE_RESTART_WIN", "scripts/windows/start_orchestrator.bat")

@dataclass
class Probe:
    name: str
    cmd: str

class RecoveryAgent:
    def __init__(self, probes: List[Probe], store: StateStore | None = None):
        self.probes = probes
        self.store = store or StateStore()

    def evaluate(self) -> Dict[str, Dict]:
        report: Dict[str, Dict] = {}
        for p in self.probes:
            ok, out = check_cmd(p.cmd)
            status = "healthy" if ok else "unhealthy"
            report[p.name] = {"status": status, "details": out[:400]}
            self.store.set_service_state(p.name, status, {"probe_cmd": p.cmd})
        return report

    def reconcile(self, platform: str = "linux") -> Dict[str, str]:
        report = self.evaluate()
        needs_recover = [n for n, r in report.items() if r["status"] == "unhealthy"]
        if not needs_recover:
            return {"action": "noop", "reason": "all healthy"}

        cmd = WINDOWS_RESTART if platform.lower().startswith("win") else LINUX_RESTART
        ok, out = check_cmd(cmd)
        result = "restarted" if ok else "restart_failed"
        for n in needs_recover:
            self.store.set_service_state(n, "restarting" if ok else "error", {"restart_cmd": cmd})
        return {"action": result, "output": out[:500], "affected": ",".join(needs_recover)}

def default_agent() -> RecoveryAgent:
    # baseline probes; adjust to your repo reality
    probes = [
        Probe(name="api_gateway", cmd="python -m py_compile api/gateway.py"),
        Probe(name="governance_imports", cmd="python -c 'import core.governance as g; print(dir(g))'"),
        Probe(name="web_build_cache", cmd="node -v")
    ]
    return RecoveryAgent(probes)
