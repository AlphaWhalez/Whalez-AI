from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from . import __init__ as _  # reserved for future pkg init
from core.telemetry.streamer import log_event

router = APIRouter()


@router.websocket("/ws/bridge")
async def ws_bridge(ws: WebSocket):
    """
    Minimal interactive session channel (text for now).
    Future: attach STT/TTS + orchestrator commands.
    """
    await ws.accept()
    await log_event("call.start", {"peer": "alpha-whalez"})
    try:
        while True:
            msg = await ws.receive_text()
            # Echo and log (placeholder)
            await log_event("call.msg", {"from": "alpha-whalez", "text": msg})
            await ws.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        pass
    finally:
        await log_event("call.end", {"peer": "alpha-whalez"})
