import inspect
from typing import Any, Callable, Dict

from core.ledger import IntentLedger
from core.telemetry.events import (
    INTENT_DONE,
    INTENT_ENQUEUE,
    INTENT_ERROR,
    INTENT_RECORDED,
    INTENT_START,
)
from core.telemetry.streamer import TelemetryStreamer

from .models import Intent, IntentStatus, IntentType


_ledger = IntentLedger()


def _normalize_result(result: Any | None) -> Dict[str, Any] | None:
    if result is None:
        return None
    if isinstance(result, dict):
        return result
    if isinstance(result, (list, tuple)):
        return {"value": list(result)}
    if isinstance(result, (str, int, float, bool)):
        return {"value": result}
    return {"value": repr(result)}


class IntentRouter:
    """
    Minimal “AI” router: maps incoming intents to handlers.
    Expandable with LLM ranking / policy later.
    """

    def __init__(self, streamer: TelemetryStreamer | None = None):
        self.streamer = streamer or TelemetryStreamer.get()
        self.handlers: Dict[IntentType, Callable[[Intent], Any]] = {}

    def register(self, intent_type: IntentType, handler: Callable[[Intent], Any]):
        self.handlers[intent_type] = handler

    async def handle(self, intent: Intent) -> Intent:
        self._record(intent, IntentStatus.ENQUEUED)
        self.streamer.emit(
            INTENT_ENQUEUE,
            {"id": intent.id, "type": intent.type.value, "payload": intent.payload},
        )
        intent.status = IntentStatus.STARTED
        self._record(intent, IntentStatus.STARTED)
        self.streamer.emit(INTENT_START, {"id": intent.id, "type": intent.type.value})

        try:
            handler = self.handlers.get(intent.type)
            if not handler:
                raise RuntimeError(f"No handler for {intent.type}")

            result = handler(intent)
            if inspect.isawaitable(result):
                result = await result
            intent.status = IntentStatus.DONE
            self._record(intent, IntentStatus.DONE, result)
            self.streamer.emit(INTENT_DONE, {"id": intent.id, "result": result})
            return intent

        except Exception as e:
            intent.status = IntentStatus.ERROR
            intent.error = str(e)
            self._record(intent, IntentStatus.ERROR, {"error": intent.error})
            self.streamer.emit(INTENT_ERROR, {"id": intent.id, "error": intent.error})
            return intent

    def _record(self, intent: Intent, status: IntentStatus, result: Any | None = None) -> None:
        normalized_result = _normalize_result(result)
        _ledger.upsert(
            id=intent.id,
            kind=intent.type.value,
            status=status.value,
            payload=intent.payload,
            result=normalized_result,
        )
        self.streamer.emit(
            INTENT_RECORDED,
            {"id": intent.id, "kind": intent.type.value, "status": status.value},
        )
