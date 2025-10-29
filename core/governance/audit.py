"""In-memory governance audit helpers for deployment workflows."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class AuditEvent:
    """Represents an auditable governance event."""

    name: str
    payload: Dict[str, object]
    timestamp: datetime


class GovernanceAuditor:
    """Stores audit events emitted during governance operations."""

    def __init__(self) -> None:
        self._events: List[AuditEvent] = []

    def record(self, name: str, payload: Optional[Dict[str, object]] = None) -> AuditEvent:
        """Persist an audit entry and return the resulting event."""

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Audit event name must be a non-empty string")
        payload = dict(payload or {})
        event = AuditEvent(name=name, payload=payload, timestamp=datetime.now(timezone.utc))
        self._events.append(event)
        return event

    def history(self) -> Iterable[AuditEvent]:
        """Return an immutable snapshot of recorded events."""

        return tuple(self._events)


__all__ = ["AuditEvent", "GovernanceAuditor"]
