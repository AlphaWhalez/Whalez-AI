"""Policy engine utilities for Whalez-AI governance."""

from __future__ import annotations

from typing import Callable, Iterable, MutableMapping, Optional


class PolicyViolation(Exception):
    """Raised when an action violates a governance policy."""


class PolicyEngine:
    """In-memory policy registry with simple enforcement hooks."""

    def __init__(self) -> None:
        self._policies: MutableMapping[str, Callable[..., bool]] = {}

    def register_policy(self, name: str, checker: Callable[..., bool]) -> None:
        """Register a policy checker callable.

        Parameters
        ----------
        name:
            The unique policy identifier.
        checker:
            Callable returning ``True`` when the policy is satisfied.
        """

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Policy name must be a non-empty string")
        if not callable(checker):
            raise TypeError("Policy checker must be callable")
        self._policies[name] = checker

    def unregister_policy(self, name: str) -> None:
        """Remove a policy from the registry if present."""

        self._policies.pop(name, None)

    def list_policies(self) -> Iterable[str]:
        """Return an iterable of registered policy names."""

        return tuple(self._policies.keys())

    def enforce(self, name: str, *args, **kwargs) -> bool:
        """Run the checker for ``name`` and raise on violation."""

        if name not in self._policies:
            raise PolicyViolation(f"Policy '{name}' is not registered")

        checker = self._policies[name]
        try:
            result = bool(checker(*args, **kwargs))
        except PolicyViolation:
            raise
        except Exception as exc:  # pragma: no cover - defensive guard
            raise PolicyViolation(
                f"Policy '{name}' raised an exception: {exc!s}"
            ) from exc

        if not result:
            raise PolicyViolation(f"Policy '{name}' rejected the operation")
        return True

    def ensure(self, name: str, fallback: Optional[Callable[[], None]] = None) -> bool:
        """Enforce a policy and optionally invoke ``fallback`` on violation."""

        try:
            return self.enforce(name)
        except PolicyViolation:
            if fallback is not None:
                fallback()
            raise


__all__ = ["PolicyEngine", "PolicyViolation"]
