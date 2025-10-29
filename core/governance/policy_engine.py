"""Policy engine utilities for Whalez-AI governance."""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional


class PolicyViolation(Exception):
    """Raised when an action violates a governance policy."""


class PolicyEngine:
    """Simple policy engine that executes registered policy callables."""

    def __init__(self, policies: Optional[Iterable[Callable[[dict], bool]]] = None) -> None:
        self._policies: List[Callable[[dict], bool]] = []
        if policies:
            for policy in policies:
                self.register_policy(policy)

    def register_policy(self, policy: Callable[[dict], bool]) -> None:
        """Register a policy callable to run during enforcement."""

        if not callable(policy):
            raise TypeError("policy must be callable")
        self._policies.append(policy)

    def enforce(self, context: Optional[dict] = None) -> bool:
        """Run all policies against the provided context."""

        context = context or {}
        for policy in self._policies:
            result = policy(context)
            if not result:
                policy_name = getattr(policy, "__name__", repr(policy))
                raise PolicyViolation(f"Policy '{policy_name}' failed for context {context!r}")
        return True


__all__ = ["PolicyEngine", "PolicyViolation"]
