import sys
from pathlib import Path

import pytest

pytest.importorskip("httpx")

from fastapi.testclient import TestClient


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.gateway import app


client = TestClient(app)


def test_reconcile_route_smoke():
    response = client.post("/governance/reconcile", json={"target": "ci-smoke"})
    assert response.status_code in (200, 201)
    data = response.json()
    assert data.get("ok") is True
    assert data.get("intent_id")
    assert data.get("name") == "reconcile"
