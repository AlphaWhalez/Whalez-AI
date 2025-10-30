
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from api.security import router as security_router
from core.controllers.orchestrator import (
    Orchestrator,
    mount_admin_console,
    router as orchestrator_router,
)
from core.tls_engine.routes import attach_tls_routes
from core.voice.bridge import router as voice_router
from api.routes import intent as intent_routes
from api.routes.console_history import router as console_history_router
from api.routes.history import router as history_router
from fastapi.middleware.cors import CORSMiddleware

gateway = FastAPI(title="Whalez-AI Unified Gateway", version="2.0")
orc = Orchestrator()

internal_api = APIRouter()
attach_tls_routes(internal_api)

gateway.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gateway.include_router(internal_api, prefix="/api")
gateway.include_router(security_router)
gateway.include_router(voice_router)
gateway.include_router(intent_routes.router)
gateway.include_router(history_router)
gateway.include_router(console_history_router)
gateway.include_router(orchestrator_router)
mount_admin_console(gateway)

class Service(BaseModel):
    name: str
    port: int
    runtime: str = "local"

@gateway.get("/api/health")
def health():
    return {"ok": True, "status": "online"}

@gateway.post("/governance/reconcile")
async def governance_reconcile(services: list[Service]):
    try:
        res = orc.reconcile([s.dict() for s in services])
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Legacy export maintained for compatibility with earlier tooling/tests.
app = gateway
