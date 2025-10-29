"""Governance deployer used by Stage 8 orchestration."""

from __future__ import annotations

from typing import Optional

from .audit import GovernanceAuditor
from .policy_engine import PolicyEngine, PolicyViolation


class GovernanceDeployer:
    """Coordinates governance checks before Stage 8 rolls out updates."""

    def __init__(self, engine: Optional[PolicyEngine] = None, auditor: Optional[GovernanceAuditor] = None) -> None:
        self.engine = engine or PolicyEngine()
        self.auditor = auditor or GovernanceAuditor()

    def preflight(self) -> None:
        """Run baseline enforcement before deployment."""

        for policy_name in self.engine.list_policies():
            self.engine.enforce(policy_name)
        self.auditor.record("governance.preflight")

    def deploy(self) -> None:
        """Perform the governance deployment."""

        try:
            self.preflight()
            self.auditor.record("governance.deploy")
        except PolicyViolation:
            self.auditor.record("governance.abort")
            raise


__all__ = ["GovernanceDeployer"]
