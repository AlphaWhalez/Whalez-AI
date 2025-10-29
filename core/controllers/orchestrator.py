"""Governance orchestrator that reconciles desired vs. actual services."""

from __future__ import annotations

import argparse
import json
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Optional

from core.governance import AuditLogger, HealthMonitor, PolicyEngine, PolicyViolation, ServiceDeployer
from core.governance.deployer import DeploymentState
from core.governance.registry import ServiceRegistry
from .adapters.local_process import LocalProcessAdapter

STATE_PATH = Path("logs/governance/state.json")
STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


class GovernanceOrchestrator:
    def __init__(self, *, dry_run: bool = True) -> None:
        self.registry = ServiceRegistry()
        self.policy = PolicyEngine()
        tls_info = self.policy.ensure_tls_ready()
        self.audit = AuditLogger()
        tls_host = tls_info.get("host") if tls_info else None
        self.health = HealthMonitor(tls_host=tls_host)
        self.adapter = LocalProcessAdapter(dry_run=dry_run)
        self.deployer = ServiceDeployer(
            adapter=self.adapter,
            policy=self.policy,
            audit=self.audit,
            health=self.health,
        )
        self.state: Dict[str, DeploymentState] = self._load_state()
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    def _load_state(self) -> Dict[str, DeploymentState]:
        if not STATE_PATH.exists():
            return {}
        payload = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        state: Dict[str, DeploymentState] = {}
        for name, data in payload.items():
            state[name] = DeploymentState(
                status=data.get("status", "unknown"),
                spec_hash=data.get("spec_hash", ""),
                strategy=data.get("strategy", "canary"),
                version_fingerprint=data.get("version_fingerprint", ""),
                active_variant=data.get("active_variant", "primary"),
                instances=data.get("instances", {}),
                last_updated=data.get("last_updated", time.time()),
                notes=data.get("notes", {}),
            )
        return state

    def _persist_state(self) -> None:
        payload = {name: state.to_dict() for name, state in self.state.items()}
        STATE_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # ------------------------------------------------------------------
    def reconcile_once(self, *, approvals: Optional[Dict[str, bool]] = None) -> Dict[str, DeploymentState]:
        approvals = approvals or {}
        self.registry.load()
        desired_services = {svc.name: svc for svc in self.registry}
        new_state: Dict[str, DeploymentState] = {}
        for service in self.registry:
            current = self.state.get(service.name)
            approved = approvals.get(service.name, False)
            try:
                deployment_state = self.deployer.reconcile(service, current, approved=approved)
            except PolicyViolation as exc:
                self.audit.emit("rollout_blocked", service.name, reason=str(exc))
                if current:
                    new_state[service.name] = current
                else:
                    new_state[service.name] = DeploymentState(
                        status="blocked",
                        spec_hash="",
                        strategy=service.rollout.strategy if service.rollout else "canary",
                        version_fingerprint="",
                        active_variant="none",
                        instances={},
                        notes={"reason": str(exc)},
                    )
                continue
            new_state[service.name] = deployment_state
        # Stop services no longer desired
        for name in set(self.state.keys()) - set(desired_services.keys()):
            entry = self.state[name]
            for variant in list(entry.instances.keys()):
                self.adapter.stop(name, variant)
            self.audit.emit("service_retired", name, reason="removed_from_config")
        self.state = new_state
        self._persist_state()
        self._emit_summary()
        return new_state

    def _emit_summary(self) -> None:
        summary_path = STATE_PATH.parent / "summary.json"
        payload = {
            "dry_run": self.dry_run,
            "services": {name: state.to_dict() for name, state in self.state.items()},
            "adapter": self.adapter.name,
            "timestamp": time.time(),
        }
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(payload, indent=2))

    # ------------------------------------------------------------------
    def run_loop(self, *, interval: float) -> None:
        print(f"Starting governance loop (interval={interval}s, dry_run={self.dry_run})")
        keep_running = True

        def _signal_handler(signum, frame):  # pragma: no cover - runtime only
            nonlocal keep_running
            keep_running = False
            print("Received signal, stopping orchestrator...")

        signal.signal(signal.SIGINT, _signal_handler)
        signal.signal(signal.SIGTERM, _signal_handler)

        while keep_running:
            self.reconcile_once()
            time.sleep(interval)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Whalez-AI governance orchestrator")
    parser.add_argument("--loop", type=float, default=0.0, help="Run reconcile loop every N seconds")
    parser.add_argument("--execute", action="store_true", help="Start real processes instead of dry-run")
    args = parser.parse_args(argv)

    orchestrator = GovernanceOrchestrator(dry_run=not args.execute)
    orchestrator.reconcile_once()
    if args.loop > 0:
        orchestrator.run_loop(interval=args.loop)
    return 0


if __name__ == "__main__":
    sys.exit(main())
