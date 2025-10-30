from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Dict, Any, List

from core.intent import Intent, IntentType, IntentRouter
from core.intent.handlers import dns_mint, console_cmd
from core.telemetry.streamer import TelemetryStreamer

router = APIRouter(prefix="/intent", tags=["intent"])

streamer = TelemetryStreamer.get()
ai = IntentRouter(streamer)
ai.register(IntentType.DNS_MINT, lambda i: dns_mint(i, streamer))
ai.register(IntentType.CONSOLE, lambda i: console_cmd(i, streamer))


class IntentIn(BaseModel):
    type: IntentType
    payload: Dict[str, Any] = Field(default_factory=dict)


@router.post("/submit")
async def submit_intent(body: IntentIn):
    intent = Intent.new(body.type, body.payload)
    result = await ai.handle(intent)
    return {"id": intent.id, "status": result.status.value, "error": result.error}


# WebSocket fanout for console
clients: List[WebSocket] = []


@router.websocket("/ws")
async def ws_intent(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep alive; no inbound control yet
    except WebSocketDisconnect:
        if ws in clients:
            clients.remove(ws)


# Ensure streamer pushes to all connected clients
@streamer.on_emit
async def _fanout(event: str, data: Dict[str, Any]):
    payload = {"event": event, "data": data}
    dead = []
    for ws in list(clients):
        try:
            await ws.send_json(payload)
        except Exception:
            dead.append(ws)
    for d in dead:
        if d in clients:
            clients.remove(d)
