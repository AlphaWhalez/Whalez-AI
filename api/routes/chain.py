import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from whalez_ai.chain import WhalezChain
from whalez_ai.crypto import verify_signed

router = APIRouter(prefix="/chain", tags=["whalezchain"])
chain = WhalezChain()


class SignedTx(BaseModel):
    payload: dict
    hash: str
    sig: str
    pub: str


@router.post("/tx/submit")
def submit_tx(tx: SignedTx):
    if not verify_signed(tx.model_dump()):
        raise HTTPException(status_code=400, detail="invalid_signature")
    return chain.submit_signed_tx(tx.model_dump())


@router.post("/internal/event")
def internal_event(kind: str, data: dict):
    return chain.submit_internal_event(kind, data)


@router.post("/blocks/maybe-build")
def maybe_build(max_txs: int = 256):
    blk = chain.build_block_if_needed(max_txs=max_txs)
    return blk or {"status": "noop"}


@router.get("/head")
def head():
    h = chain.store.head()
    if not h:
        return {"height": -1}
    return {
        "id": h[0],
        "height": h[1],
        "prev_hash": h[2],
        "merkle_root": h[3],
        "header_hash": h[4],
        "header_sig": h[5],
        "pub": h[6],
        "ts": h[7],
    }


@router.get("/tx/{tx_hash}")
def get_tx(tx_hash: str):
    cur = chain.store.db.execute(
        """
      SELECT t.tx_hash,t.payload_json,t.sig,t.pub,r.block_id,r.block_hash,r.merkle_proof_json
      FROM chain_txs t LEFT JOIN chain_tx_receipts r ON t.tx_hash=r.tx_hash WHERE t.tx_hash=?
      """,
        (tx_hash,),
    )
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "not_found")
    return {
        "tx_hash": row[0],
        "payload": json.loads(row[1]),
        "sig": row[2],
        "pub": row[3],
        "receipt": None
        if row[4] is None
        else {
            "block_id": row[4],
            "block_hash": row[5],
            "proof": json.loads(row[6]),
        },
    }
