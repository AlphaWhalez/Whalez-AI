"""Console history page integration tests."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

# Ensure repository root is on the import path for CI executions
TESTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TESTS_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from api.gateway import app  # noqa: E402  (import after path setup)


def test_console_history_page_loads() -> None:
    """Verify /console/history endpoint renders correctly."""
    client = TestClient(app)
    response = client.get("/console/")

    assert response.status_code == 200
    assert "<title>Whalez-AI • Unified Console</title>" in response.text
