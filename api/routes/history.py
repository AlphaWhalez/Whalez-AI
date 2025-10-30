from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException

from core.ledger import IntentLedger, IntentNotFound
from core.telemetry.events import INTENT_RECALLED, INTENT_REPLAYED
from core.telemetry.streamer import TelemetryStreamer

router = APIRouter(prefix="/intent", tags=["intent-history"])
ledger = IntentLedger()
streamer = TelemetryStreamer.get()
DRY_RUN = os.getenv("DRY_RUN", "1") == "1"


@router.get("/history")
def list_history(limit: int = 100, kind: str | None = None, status: str | None = None):
    rows = ledger.list(limit=limit, kind=kind, status=status)
    streamer.emit(INTENT_RECALLED, {"count": len(rows)})
    return {"items": rows}


@router.get("/history/{intent_id}")
def get_record(intent_id: str):
    try:
        row = ledger.get(intent_id)
    except IntentNotFound as exc:  # pragma: no cover - handled below
        raise HTTPException(status_code=404, detail="Intent not found") from exc
    streamer.emit(INTENT_RECALLED, {"id": intent_id})
    return row


@router.post("/replay/{intent_id}")
def replay(intent_id: str):
    try:
        row = ledger.get(intent_id)
    except IntentNotFound as exc:  # pragma: no cover - handled below
        raise HTTPException(status_code=404, detail="Intent not found") from exc

    if DRY_RUN:
        action = {"replayed": intent_id, "mode": "dry-run", "payload": row["payload"]}
        streamer.emit(INTENT_REPLAYED, action)
        return {"ok": True, "dry_run": True, "action": action}

    action = {"replayed": intent_id, "mode": "live-not-implemented"}
    streamer.emit(INTENT_REPLAYED, action)
    return {"ok": True, "dry_run": False, "action": action}
