import os
os.environ.setdefault("DRY_RUN", "1")

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
from api.gateway import app

client = TestClient(app)


def test_submit_console_intent():
    r = client.post("/intent/submit", json={"type": "console", "payload": {"cmd": "echo 'hi'"}})
    assert r.status_code == 200
    j = r.json()
    assert j["status"] in ("done", "DONE") or j["status"] == "done"


def test_submit_dns_intent_simulated():
    r = client.post("/intent/submit", json={"type": "dns_mint", "payload": {"sub": "ai-boot"}})
    assert r.status_code == 200
    assert r.json()["status"] == "done"
