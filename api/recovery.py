from fastapi import APIRouter, Depends
from typing import Any, Dict
from core.orchestrator.recovery_agent import default_agent
from core.security.auth import require_scope  # already added in Phase-C

router = APIRouter(prefix="/recovery", tags=["recovery"])

@router.get("/status", dependencies=[Depends(require_scope("ops:read"))])
def status() -> Dict[str, Any]:
    return default_agent().evaluate()

@router.post("/reconcile", dependencies=[Depends(require_scope("ops:write"))])
def reconcile() -> Dict[str, Any]:
    return default_agent().reconcile()
