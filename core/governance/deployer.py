"""Deployment helpers that integrate with the governance policy engine."""
from __future__ import annotations

from typing import Callable, Optional

from .policy_engine import PolicyEngine, PolicyViolation


class ServiceDeployer:
    """Coordinates service deployments with governance enforcement."""

    def __init__(self, policy_engine: PolicyEngine) -> None:
        self._policy_engine = policy_engine

    def deploy(self, deploy_callable: Callable[[], object], context: Optional[dict] = None) -> object:
        """Run the provided deployment callable after enforcing policies."""

        self._policy_engine.enforce(context)
        return deploy_callable()

    def safe_deploy(self, deploy_callable: Callable[[], object], context: Optional[dict] = None) -> object:
        """Run deployment and capture policy violations as exceptions."""

        try:
            return self.deploy(deploy_callable, context=context)
        except PolicyViolation:
            raise


__all__ = ["ServiceDeployer"]
