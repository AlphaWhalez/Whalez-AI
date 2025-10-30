import inspect
from typing import Callable, Dict, Any
from .models import Intent, IntentType, IntentStatus
from core.telemetry.streamer import TelemetryStreamer


class IntentRouter:
    """
    Minimal “AI” router: maps incoming intents to handlers.
    Expandable with LLM ranking / policy later.
    """

    def __init__(self, streamer: TelemetryStreamer):
        self.streamer = streamer
        self.handlers: Dict[IntentType, Callable[[Intent], Any]] = {}

    def register(self, intent_type: IntentType, handler: Callable[[Intent], Any]):
        self.handlers[intent_type] = handler

    async def handle(self, intent: Intent) -> Intent:
        self.streamer.emit("intent.enqueue", {"id": intent.id, "type": intent.type.value})
        intent.status = IntentStatus.STARTED
        self.streamer.emit("intent.start", {"id": intent.id})

        try:
            handler = self.handlers.get(intent.type)
            if not handler:
                raise RuntimeError(f"No handler for {intent.type}")

            result = handler(intent)
            if inspect.isawaitable(result):
                result = await result
            intent.status = IntentStatus.DONE
            self.streamer.emit("intent.done", {"id": intent.id, "result": result})
            return intent

        except Exception as e:
            intent.status = IntentStatus.ERROR
            intent.error = str(e)
            self.streamer.emit("intent.error", {"id": intent.id, "error": intent.error})
            return intent
