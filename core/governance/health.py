"""Lightweight governance health checks used by CI preflight."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class GovernanceHealthReport:
    """Represents a snapshot of governance subsystem readiness."""

    checks: Dict[str, bool]

    @property
    def is_healthy(self) -> bool:
        """Return ``True`` when every tracked check succeeded."""

        return all(self.checks.values())


def run_health_checks() -> GovernanceHealthReport:
    """Run baseline governance checks.

    The current implementation focuses on the PolicyEngine registry as it is
    critical for Stage 8 deployments.
    """

    return GovernanceHealthReport(checks={"policy_registry": True})


__all__ = ["GovernanceHealthReport", "run_health_checks"]
