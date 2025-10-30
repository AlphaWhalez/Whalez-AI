from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time, uuid


class IntentType(str, Enum):
    DNS_MINT = "dns_mint"
    CONSOLE = "console"
    SYSTEM = "system"


class IntentStatus(str, Enum):
    ENQUEUED = "enqueued"
    STARTED = "started"
    DONE = "done"
    ERROR = "error"


@dataclass
class Intent:
    id: str
    type: IntentType
    payload: Dict[str, Any]
    created_at: float = field(default_factory=lambda: time.time())
    status: IntentStatus = IntentStatus.ENQUEUED
    error: Optional[str] = None

    @staticmethod
    def new(type: IntentType, payload: Dict[str, Any]) -> "Intent":
        return Intent(id=str(uuid.uuid4()), type=type, payload=payload)
