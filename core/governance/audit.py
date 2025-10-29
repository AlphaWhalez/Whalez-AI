"""Audit logging helpers for governance events."""
from __future__ import annotations

import logging
from typing import Any, Optional


class AuditLogger:
    """Lightweight audit logger used during governance operations."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger("core.governance.audit")

    def log_policy_violation(self, violation: Exception, context: Optional[dict] = None) -> None:
        """Record a policy violation along with optional contextual metadata."""

        context = context or {}
        self._logger.warning("Policy violation detected: %s; context=%s", violation, context)

    def log_event(self, message: str, **metadata: Any) -> None:
        """Record a governance event with structured metadata."""

        self._logger.info("Governance event: %s; metadata=%s", message, metadata)


__all__ = ["AuditLogger"]
