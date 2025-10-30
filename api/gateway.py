
import asyncio
from typing import Optional

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from api.security import router as security_router
from core.controllers.orchestrator import Orchestrator, request_reconcile
from core.telemetry.streamer import router as telemetry_router
from core.tls_engine.routes import attach_tls_routes
from core.voice.bridge import router as voice_router
from core.webui.routes import router as webui_router

app = FastAPI(title="Whalez-AI Gateway")
orc = Orchestrator()

router = APIRouter()
attach_tls_routes(router)
app.include_router(router, prefix="/api")
app.include_router(security_router)
app.include_router(telemetry_router)
app.include_router(voice_router)
app.include_router(webui_router)

class Service(BaseModel):
    name: str
    port: int
    runtime: str = "local"


class GovernanceReconcileRequest(BaseModel):
    target: Optional[str] = None
    services: Optional[list[Service]] = None


@app.get("/api/health")
def health():
    return {"ok": True, "status": "online"}


@app.post("/governance/reconcile")
async def governance_reconcile(payload: GovernanceReconcileRequest):
    if payload.services:
        try:
            loop = asyncio.get_running_loop()
            res = await loop.run_in_executor(
                None, lambda: orc.reconcile([s.dict() for s in payload.services or []])
            )
            return res
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    target = payload.target or "dummy-service"
    return await request_reconcile(target=target)
