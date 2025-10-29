"""Audit logging for governance actions."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

AUDIT_DIR = Path("logs/audit")
AUDIT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class AuditEvent:
    ts: float
    event: str
    service: str
    details: Dict[str, object]

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


class AuditLogger:
    def __init__(self, *, namespace: str = "deploy") -> None:
        self.namespace = namespace
        self.path = self._resolve_path()

    def _resolve_path(self) -> Path:
        stamp = time.strftime("%Y%m%d")
        return AUDIT_DIR / f"{self.namespace}_{stamp}.jsonl"

    def emit(self, event: str, service: str, **details: object) -> AuditEvent:
        record = AuditEvent(ts=time.time(), event=event, service=service, details=details)
        line = record.to_json()
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        return record

    def tail(self, limit: int = 100) -> List[AuditEvent]:
        events: List[AuditEvent] = []
        if not self.path.exists():
            return events
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh.readlines()[-limit:]:
                payload = json.loads(line)
                events.append(
                    AuditEvent(
                        ts=payload.get("ts", 0.0),
                        event=payload.get("event", "unknown"),
                        service=payload.get("service", "unknown"),
                        details=payload.get("details", {}),
                    )
                )
        return events

    def as_dicts(self, limit: int = 100) -> List[Dict[str, object]]:
        return [asdict(event) for event in self.tail(limit)]


__all__ = ["AuditLogger", "AuditEvent"]
