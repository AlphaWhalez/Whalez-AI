import os
import sys
from pathlib import Path

os.environ["INTENT_LEDGER_PATH"] = "data/test_api.sqlite3"
os.environ["DRY_RUN"] = "1"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from api.gateway import app
from api.routes import history as history_routes
from core.ledger import IntentLedger


def test_history_list_and_detail(tmp_path):
    os.environ["INTENT_LEDGER_PATH"] = str(tmp_path / "ledger.sqlite3")
    history_routes.ledger = IntentLedger()
    history_routes.streamer = history_routes.TelemetryStreamer.get()
    ledger = history_routes.ledger
    ledger.upsert(
        id="z1", kind="dns.mint", status="done", payload={"y": 2}, result={"ok": True}
    )
    client = TestClient(app)
    assert client.get("/intent/history").status_code == 200
    response = client.get("/intent/history/z1")
    assert response.status_code == 200
    assert response.json()["id"] == "z1"


def test_replay_dry_run(tmp_path):
    os.environ["INTENT_LEDGER_PATH"] = str(tmp_path / "ledger.sqlite3")
    history_routes.ledger = IntentLedger()
    history_routes.streamer = history_routes.TelemetryStreamer.get()
    ledger = history_routes.ledger
    ledger.upsert(id="r1", kind="dns.mint", status="done", payload={"n": 9})
    client = TestClient(app)
    response = client.post("/intent/replay/r1")
    data = response.json()
    assert response.status_code == 200
    assert data["dry_run"] is True
    assert data["action"]["replayed"] == "r1"
