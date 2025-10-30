import os
import sys
from pathlib import Path

os.environ["INTENT_LEDGER_PATH"] = "data/test_ledger.sqlite3"

sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.ledger import IntentLedger


def test_upsert_and_get_roundtrip(tmp_path):
    os.environ["INTENT_LEDGER_PATH"] = str(tmp_path / "ledger.sqlite3")
    ledger = IntentLedger()
    ledger.upsert(id="abc", kind="dns.mint", status="queued", payload={"x": 1})
    row = ledger.get("abc")
    assert row["id"] == "abc"
    assert row["kind"] == "dns.mint"
    assert row["status"] == "queued"
