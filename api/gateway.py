
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from core.controllers.orchestrator import Orchestrator

app = FastAPI(title="Whalez-AI Gateway")
orc = Orchestrator()

class Service(BaseModel):
    name: str
    port: int
    runtime: str = "local"

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/governance/reconcile")
def governance_reconcile(services: list[Service]):
    try:
        res = orc.reconcile([s.dict() for s in services])
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
