from fastapi.testclient import TestClient

from api.gateway import app


def test_console_history_page_loads():
    client = TestClient(app)
    response = client.get("/console/history")
    assert response.status_code == 200
    assert "<title>Whalez-AI Intent History</title>" in response.text
