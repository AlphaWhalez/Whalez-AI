
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from api import recovery as recovery_api
from api.security import router as security_router
from core.controllers.orchestrator import Orchestrator
from core.tls_engine.routes import attach_tls_routes

app = FastAPI(title="Whalez-AI Gateway")
orc = Orchestrator()

router = APIRouter()
attach_tls_routes(router)
app.include_router(router, prefix="/api")
app.include_router(security_router)
app.include_router(recovery_api.router)

class Service(BaseModel):
    name: str
    port: int
    runtime: str = "local"

@app.get("/api/health")
def health():
    return {"ok": True, "status": "online"}

@app.post("/governance/reconcile")
def governance_reconcile(services: list[Service]):
    try:
        res = orc.reconcile([s.dict() for s in services])
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
