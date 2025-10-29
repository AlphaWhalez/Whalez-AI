from __future__ import annotations
import asyncio
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from datetime import datetime

router = APIRouter()
_clients: Set[WebSocket] = set()
_queue: "asyncio.Queue[str]" = asyncio.Queue()


async def _fanout():
    while True:
        msg = await _queue.get()
        dead = []
        for ws in list(_clients):
            try:
                await ws.send_text(msg)
            except Exception:
                dead.append(ws)
        for ws in dead:
            try:
                _clients.remove(ws)
            except KeyError:
                pass


# single background task handle
_fanout_task: asyncio.Task | None = None


def _ensure_fanout():
    global _fanout_task
    loop = asyncio.get_event_loop()
    if _fanout_task is None or _fanout_task.done():
        _fanout_task = loop.create_task(_fanout())


async def log_event(kind: str, data: dict | str):
    """
    Safe, structured log for UI. Never raises.
    """
    try:
        _ensure_fanout()
        if not isinstance(data, str):
            import json
            payload = json.dumps({"t": datetime.utcnow().isoformat() + "Z", "k": kind, "d": data})
        else:
            payload = data
        await _queue.put(payload)
    except Exception:
        # swallow: logging must never break business logic
        pass


@router.websocket("/ws/stream")
async def ws_stream(ws: WebSocket):
    await ws.accept()
    _ensure_fanout()
    _clients.add(ws)
    try:
        while True:
            # keepalive (client can send pings if it wants)
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if ws in _clients:
            _clients.remove(ws)
