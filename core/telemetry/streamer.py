"""Unified event streamer for the Whalez-AI consoles."""

from __future__ import annotations

import asyncio
import json
import random
from typing import Dict

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


async def log_event(kind: str, data: dict | str) -> None:
    """Fan out structured orchestrator events to connected consoles."""
    try:
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
        await _broadcast(payload)
    except Exception:
        # Streaming must never interfere with business logic
        return None


async def stream_events(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    _ensure_lock(websocket)
    try:
        while True:
            event = {
                "event": "pulse",
                "signal": random.choice(["INTENT_START", "INTENT_DONE", "DNS_MINTED"]),
                "timestamp": asyncio.get_event_loop().time(),
            }
            await _send(websocket, json.dumps(event))
            await asyncio.sleep(2)
    except Exception:
        pass
    finally:
        clients.discard(websocket)
        _client_locks.pop(websocket, None)
