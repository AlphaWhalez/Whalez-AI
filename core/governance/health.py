"""Health monitoring utilities for governance-aware services."""
from __future__ import annotations

from typing import Callable, Dict, List


class HealthMonitor:
    """Collects and executes health checks."""

    def __init__(self) -> None:
        self._checks: List[Callable[[], bool]] = []

    def add_check(self, check: Callable[[], bool]) -> None:
        """Register a new health check callable."""

        if not callable(check):
            raise TypeError("health check must be callable")
        self._checks.append(check)

    def run_checks(self) -> Dict[str, bool]:
        """Execute all registered health checks and return their results."""

        results: Dict[str, bool] = {}
        for check in self._checks:
            name = getattr(check, "__name__", repr(check))
            results[name] = bool(check())
        return results


__all__ = ["HealthMonitor"]
