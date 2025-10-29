"""Deployment strategies for the governance orchestrator."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

from .audit import AuditLogger
from .health import HealthMonitor
from .policy_engine import PolicyEngine, PolicyViolation
from .registry import ServiceDefinition, ServiceRolloutConfig


@dataclass
class DeploymentState:
    status: str
    spec_hash: str
    strategy: str
    version_fingerprint: str
    active_variant: str = "primary"
    instances: Dict[str, Dict[str, object]] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    notes: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "spec_hash": self.spec_hash,
            "strategy": self.strategy,
            "version_fingerprint": self.version_fingerprint,
            "active_variant": self.active_variant,
            "instances": self.instances,
            "last_updated": self.last_updated,
            "notes": self.notes,
        }


class ServiceDeployer:
    def __init__(
        self,
        *,
        adapter,
        policy: PolicyEngine,
        audit: AuditLogger,
        health: HealthMonitor,
    ) -> None:
        self.adapter = adapter
        self.policy = policy
        self.audit = audit
        self.health = health

    # ------------------------------------------------------------------
    def _fingerprint(self, service: ServiceDefinition) -> str:
        payload = {
            "command": service.command,
            "env": service.env,
            "ports": service.ports,
            "strategy": service.rollout.strategy if service.rollout else "canary",
        }
        raw = json.dumps(payload, sort_keys=True).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()

    def _rollout_config(self, service: ServiceDefinition) -> ServiceRolloutConfig:
        return service.rollout or ServiceRolloutConfig()

    # ------------------------------------------------------------------
    def reconcile(
        self,
        service: ServiceDefinition,
        current_state: Optional[DeploymentState],
        *,
        approved: bool = False,
    ) -> DeploymentState:
        self.policy.validate_adapter(self.adapter.name)
        spec_hash = self._fingerprint(service)
        rollout = self._rollout_config(service)
        version_fingerprint = spec_hash
        if current_state and current_state.spec_hash == spec_hash:
            # nothing to do, but refresh last seen metrics
            current_state.last_updated = time.time()
            return current_state

        # Determine version transition guard
        current_version = current_state.notes.get("version") if current_state else None
        desired_version = service.env.get("VERSION") if service.env else None
        self.policy.guard_version_transition(
            service=service.name,
            current_version=current_version,
            next_version=desired_version,
            approved=approved,
        )
        self.policy.check_rollout_limits(active_rollouts=1)

        if not current_state:
            new_state = self._initial_start(service, spec_hash, version_fingerprint, rollout)
        else:
            if rollout.strategy == "blue-green":
                new_state = self._rollout_blue_green(
                    service, current_state, spec_hash, version_fingerprint, rollout
                )
            elif rollout.strategy == "canary":
                new_state = self._rollout_canary(
                    service, current_state, spec_hash, version_fingerprint, rollout
                )
            else:
                raise PolicyViolation(f"unknown rollout strategy '{rollout.strategy}'")
        previous_version = current_state.notes.get("version") if current_state else None
        if desired_version or previous_version:
            new_state.notes["version"] = desired_version or previous_version
        return new_state

    # ------------------------------------------------------------------
    def _initial_start(
        self,
        service: ServiceDefinition,
        spec_hash: str,
        version_fingerprint: str,
        rollout: ServiceRolloutConfig,
    ) -> DeploymentState:
        self.audit.emit("service_start", service.name, strategy="initial", adapter=self.adapter.name)
        instance = self.adapter.start(service, variant="primary")
        healthy, report = self.health.wait_for_healthy(service, instance, rollout.pause_seconds)
        if not healthy:
            self.audit.emit("service_start_failed", service.name, report=report)
            self.adapter.stop(service.name, variant="primary")
            return DeploymentState(
                status="failed",
                spec_hash=spec_hash,
                strategy=rollout.strategy,
                version_fingerprint=version_fingerprint,
                active_variant="none",
                instances={},
                notes={"last_error": report},
            )
        self.audit.emit("service_running", service.name, report=report)
        return DeploymentState(
            status="running",
            spec_hash=spec_hash,
            strategy=rollout.strategy,
            version_fingerprint=version_fingerprint,
            active_variant="primary",
            instances={"primary": instance},
            notes={"slo": report},
        )

    # ------------------------------------------------------------------
    def _rollout_blue_green(
        self,
        service: ServiceDefinition,
        current_state: DeploymentState,
        spec_hash: str,
        version_fingerprint: str,
        rollout: ServiceRolloutConfig,
    ) -> DeploymentState:
        active = current_state.active_variant or "blue"
        standby = "green" if active == "blue" else "blue"
        self.audit.emit(
            "rollout_started",
            service.name,
            strategy="blue-green",
            active_variant=active,
            standby_variant=standby,
        )
        instance = self.adapter.start(service, variant=standby)
        healthy, report = self.health.wait_for_healthy(service, instance, rollout.pause_seconds)
        if not healthy:
            self.audit.emit("rollout_aborted", service.name, strategy="blue-green", reason="health_failed", report=report)
            self.adapter.stop(service.name, variant=standby)
            current_state.notes["last_error"] = report
            current_state.last_updated = time.time()
            return current_state
        # Promote standby
        self.adapter.promote(service.name, source_variant=standby, target_variant="primary")
        if current_state.instances.get(active):
            self.adapter.stop(service.name, variant=active)
        self.audit.emit(
            "rollout_completed",
            service.name,
            strategy="blue-green",
            promoted_variant=standby,
            report=report,
        )
        instances = {"primary": instance}
        return DeploymentState(
            status="running",
            spec_hash=spec_hash,
            strategy=rollout.strategy,
            version_fingerprint=version_fingerprint,
            active_variant=standby,
            instances=instances,
            notes={"slo": report},
        )

    # ------------------------------------------------------------------
    def _rollout_canary(
        self,
        service: ServiceDefinition,
        current_state: DeploymentState,
        spec_hash: str,
        version_fingerprint: str,
        rollout: ServiceRolloutConfig,
    ) -> DeploymentState:
        self.audit.emit(
            "rollout_started",
            service.name,
            strategy="canary",
            canary_percent=rollout.canary_percent,
        )
        canary = self.adapter.start(service, variant="canary")
        healthy, report = self.health.wait_for_healthy(service, canary, rollout.pause_seconds)
        if not healthy:
            self.audit.emit(
                "rollout_aborted",
                service.name,
                strategy="canary",
                reason="health_failed",
                report=report,
            )
            self.adapter.stop(service.name, variant="canary")
            current_state.notes["last_error"] = report
            current_state.last_updated = time.time()
            return current_state
        # Promote canary to primary
        old_primary = current_state.instances.get("primary")
        if old_primary:
            self.adapter.stop(service.name, variant="primary")
        promoted = self.adapter.promote(service.name, source_variant="canary", target_variant="primary")
        self.audit.emit(
            "rollout_completed",
            service.name,
            strategy="canary",
            report=report,
        )
        return DeploymentState(
            status="running",
            spec_hash=spec_hash,
            strategy=rollout.strategy,
            version_fingerprint=version_fingerprint,
            active_variant="primary",
            instances={"primary": promoted},
            notes={"slo": report},
        )


__all__ = ["ServiceDeployer", "DeploymentState"]
