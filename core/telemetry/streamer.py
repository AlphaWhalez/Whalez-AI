"""Unified event streamer for the Whalez-AI consoles."""

from __future__ import annotations

import asyncio
import inspect
import json
import random
from typing import Any, Awaitable, Callable, Dict

from fastapi import WebSocket

clients: set[WebSocket] = set()
_client_locks: Dict[WebSocket, asyncio.Lock] = {}
_broadcast_gate = asyncio.Lock()


def _ensure_lock(websocket: WebSocket) -> asyncio.Lock:
    lock = _client_locks.get(websocket)
    if lock is None:
        lock = asyncio.Lock()
        _client_locks[websocket] = lock
    return lock


async def _send(websocket: WebSocket, payload: str) -> None:
    lock = _ensure_lock(websocket)
    async with lock:
        await websocket.send_text(payload)


async def _broadcast(payload: str) -> None:
    async with _broadcast_gate:
        dead: list[WebSocket] = []
        for ws in list(clients):
            try:
                await _send(ws, payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            clients.discard(ws)
            _client_locks.pop(ws, None)


def _normalize_signal(kind: str) -> str:
    token = kind.replace(".", "_")
    return token.upper()


def _schedule(coro: Awaitable[Any]) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(coro)
        return
    loop.create_task(coro)


def _serialize_event(kind: str, data: Any) -> str:
    loop = asyncio.get_event_loop()
    timestamp = loop.time()
    event = {
        "event": kind,
        "signal": _normalize_signal(kind),
        "data": data,
        "timestamp": timestamp,
    }
    try:
        payload = json.dumps(event)
    except TypeError:
        event = {
            "event": kind,
            "signal": _normalize_signal(kind),
            "data": repr(data),
            "timestamp": timestamp,
        }
        payload = json.dumps(event)
    return payload


class TelemetryStreamer:
    """Fan-out utility that supports synchronous emits with async listeners."""

    def __init__(self) -> None:
        self._listeners: list[Callable[[str, Any], Any]] = []

    @staticmethod
    def get() -> "TelemetryStreamer":
        """Return the shared default streamer instance."""
        return _default_streamer

    def on_emit(self, func: Callable[[str, Any], Any]) -> Callable[[str, Any], Any]:
        self._listeners.append(func)
        return func

    def emit(self, kind: str, data: Any) -> None:
        for listener in list(self._listeners):
            try:
                result = listener(kind, data)
                if inspect.isawaitable(result):
                    _schedule(result)
            except Exception:
                continue


_default_streamer = TelemetryStreamer()


@_default_streamer.on_emit
def _fanout_default(kind: str, data: Any) -> None:
    payload = _serialize_event(kind, data)
    _schedule(_broadcast(payload))


async def log_event(kind: str, data: dict | str) -> None:
    """Fan out structured orchestrator events to connected consoles."""
    _default_streamer.emit(kind, data)


async def stream_events(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    _ensure_lock(websocket)
    try:
        loop = asyncio.get_event_loop()
        await _send(
            websocket,
            json.dumps(
                {
                    "event": "connected",
                    "signal": "CONSOLE_CONNECTED",
                    "timestamp": loop.time(),
                }
            ),
        )
        while True:
            event = {
                "event": "pulse",
                "signal": random.choice(["INTENT_START", "INTENT_DONE", "DNS_MINTED"]),
                "timestamp": loop.time(),
            }
            await _broadcast(json.dumps(event))
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        raise
    except Exception:
        pass
    finally:
        clients.discard(websocket)
        _client_locks.pop(websocket, None)
