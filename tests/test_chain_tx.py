from whalez_ai.chain import WhalezChain


def test_tx_block_roundtrip(tmp_path):
    c = WhalezChain(db_path=str(tmp_path / "w.db"), key_path=str(tmp_path / ".k"))
    signed = c.submit_internal_event("unit.test", {"ok": True})
    assert "hash" in signed
    blk = c.build_block_if_needed()
    assert blk and "header_hash" in blk
