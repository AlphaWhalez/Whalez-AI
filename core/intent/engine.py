from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from core.telemetry.streamer import emit  # type: ignore
except Exception:  # pragma: no cover - defensive fallback
    def emit(event: str, data: Dict[str, Any]) -> None:  # type: ignore
        return None


@dataclass
class Intent:
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    status: str = "queued"
    created_at: float = field(default_factory=lambda: time.time())
    started_at: Optional[float] = None
    finished_at: Optional[float] = None


class IntentEngine:
    """Async, minimal intent engine with lifecycle signaling."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Intent] = asyncio.Queue()
        self._running: Dict[str, Intent] = {}
        self._done: Dict[str, Intent] = {}
        self._worker_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        if self._worker_task and not self._worker_task.done():
            return
        self._worker_task = asyncio.create_task(self._worker(), name="intent-engine-worker")

    async def _worker(self) -> None:
        while True:
            intent = await self._queue.get()
            try:
                await self._start_intent(intent)
                await asyncio.sleep(0)
                await self._finish_intent(intent, success=True)
            except Exception as exc:  # pragma: no cover
                await self._finish_intent(intent, success=False, error=str(exc))
            finally:
                self._queue.task_done()

    async def enqueue(self, name: str, payload: Optional[Dict[str, Any]] = None) -> Intent:
        payload = payload or {}
        intent = Intent(name=name, payload=payload)
        await self._queue.put(intent)
        emit("intent.enqueue", {"id": intent.id, "name": intent.name, "payload": intent.payload})
        await self.start()
        return intent

    async def _start_intent(self, intent: Intent) -> None:
        async with self._lock:
            intent.status = "running"
            intent.started_at = time.time()
            self._running[intent.id] = intent
        emit("intent.start", {"id": intent.id, "name": intent.name})

    async def _finish_intent(self, intent: Intent, *, success: bool, error: Optional[str] = None) -> None:
        async with self._lock:
            intent.status = "done" if success else "error"
            intent.finished_at = time.time()
            self._running.pop(intent.id, None)
            self._done[intent.id] = intent
        emit("intent.done", {"id": intent.id, "name": intent.name, "success": success, "error": error})

    async def reconcile(self, target: str = "dummy-service") -> Intent:
        return await self.enqueue("reconcile", {"target": target})


_global_engine: Optional[IntentEngine] = None


def get_engine() -> IntentEngine:
    global _global_engine
    if _global_engine is None:
        _global_engine = IntentEngine()
    return _global_engine
