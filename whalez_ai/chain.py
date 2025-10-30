import json
import sqlite3
import time
from typing import List, Optional, Tuple

from .crypto import canonical, load_or_create_node_key, sha256, sign_dict, verify_signed

SCHEMA = """
CREATE TABLE IF NOT EXISTS chain_blocks(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  height INTEGER NOT NULL UNIQUE,
  prev_hash TEXT,
  merkle_root TEXT NOT NULL,
  header_hash TEXT NOT NULL,
  header_sig TEXT NOT NULL,
  pub TEXT NOT NULL,
  ts INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS chain_txs(
  tx_hash TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  sig TEXT NOT NULL,
  pub TEXT NOT NULL,
  block_id INTEGER,
  FOREIGN KEY(block_id) REFERENCES chain_blocks(id)
);
CREATE TABLE IF NOT EXISTS chain_tx_receipts(
  tx_hash TEXT PRIMARY KEY,
  block_id INTEGER NOT NULL,
  block_hash TEXT NOT NULL,
  merkle_proof_json TEXT NOT NULL
);
"""


def merkle_root(hashes: List[str]) -> str:
    if not hashes:
        return sha256(b"")
    layer = hashes[:]
    while len(layer) > 1:
        nxt = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            nxt.append(sha256((a + b).encode()))
        layer = nxt
    return layer[0]


class ChainStore:
    def __init__(self, path="whalezchain.db"):
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.db.executescript(SCHEMA)
        self.db.commit()

    def head(self) -> Optional[Tuple]:
        cur = self.db.execute("SELECT * FROM chain_blocks ORDER BY height DESC LIMIT 1")
        return cur.fetchone()

    def next_height(self) -> int:
        h = self.head()
        return (h[1] + 1) if h else 0

    def put_tx(self, signed: dict):
        # idempotent insert
        self.db.execute(
            "INSERT OR IGNORE INTO chain_txs(tx_hash,payload_json,sig,pub,block_id) VALUES(?,?,?,?,NULL)",
            (signed["hash"], json.dumps(signed["payload"]), signed["sig"], signed["pub"]),
        )
        self.db.commit()

    def pending_txs(self, limit=1000) -> List[Tuple[str]]:
        cur = self.db.execute(
            "SELECT tx_hash FROM chain_txs WHERE block_id IS NULL LIMIT ?", (limit,)
        )
        return [r[0] for r in cur.fetchall()]

    def get_tx_payloads(self, tx_hashes: List[str]) -> List[dict]:
        q = "SELECT tx_hash,payload_json,sig,pub FROM chain_txs WHERE tx_hash IN (%s)" % ",".join(
            "?" * len(tx_hashes)
        )
        cur = self.db.execute(q, tx_hashes)
        return [
            {"tx_hash": h, "payload": json.loads(p), "sig": s, "pub": pb}
            for h, p, s, pb in cur.fetchall()
        ]

    def commit_block(
        self,
        tx_hashes: List[str],
        node_sig: str,
        node_pub: str,
        header_hash: str,
        merkle: str,
        ts: int,
    ):
        height = self.next_height()
        prev_head = self.head()
        prev = prev_head[4] if prev_head else None
        cur = self.db.execute(
            "INSERT INTO chain_blocks(height,prev_hash,merkle_root,header_hash,header_sig,pub,ts) VALUES(?,?,?,?,?,?,?)",
            (height, prev, merkle, header_hash, node_sig, node_pub, ts),
        )
        block_id = cur.lastrowid
        self.db.executemany(
            "UPDATE chain_txs SET block_id=? WHERE tx_hash=?",
            [(block_id, h) for h in tx_hashes],
        )
        # receipts (simple merkle single-path proofs)
        proofs = build_merkle_proofs(tx_hashes)
        for h, path in proofs.items():
            self.db.execute(
                "INSERT OR REPLACE INTO chain_tx_receipts(tx_hash,block_id,block_hash,merkle_proof_json) VALUES(?,?,?,?)",
                (h, block_id, header_hash, json.dumps(path)),
            )
        self.db.commit()
        return block_id, height


def build_merkle_proofs(hashes: List[str]) -> dict:
    # returns {tx_hash: [{"side":"L|R","hash":...}, ...]}
    if not hashes:
        return {}
    layers = [hashes[:]]
    while len(layers[-1]) > 1:
        cur = layers[-1]
        nxt = []
        for i in range(0, len(cur), 2):
            a = cur[i]
            b = cur[i + 1] if i + 1 < len(cur) else cur[i]
            nxt.append(sha256((a + b).encode()))
        layers.append(nxt)
    proofs = {h: [] for h in hashes}
    # walk up
    for depth in range(len(layers) - 1):
        cur = layers[depth]
        for i, h in enumerate(cur):
            pair_i = i + 1 if i % 2 == 0 else i - 1
            pair = cur[pair_i] if pair_i < len(cur) else h
            side = "R" if i % 2 == 0 else "L"
            proofs[h].append({"side": side, "hash": pair})
    return proofs


# Public interface
class WhalezChain:
    def __init__(self, db_path="whalezchain.db", key_path=".node_ed25519.key"):
        self.store = ChainStore(db_path)
        self.sk = load_or_create_node_key(key_path)

    def submit_internal_event(self, kind: str, data: dict) -> dict:
        payload = {"kind": kind, "ts": int(time.time()), "data": data}
        signed = sign_dict(self.sk, payload)
        self.store.put_tx(signed)
        return signed

    def submit_signed_tx(self, signed: dict):
        assert verify_signed(signed), "invalid_signature"
        self.store.put_tx(signed)
        return {"accepted": True, "tx_hash": signed["hash"]}

    def build_block_if_needed(self, max_txs=256) -> Optional[dict]:
        txs = self.store.pending_txs(limit=max_txs)
        if not txs:
            return None
        prev_head = self.store.head()
        merkle = merkle_root(txs)
        header = {
            "prev": prev_head[4] if prev_head else None,
            "merkle": merkle,
            "ts": int(time.time()),
            "height": self.store.next_height(),
        }
        header_hash = sha256(canonical(header))
        signed_header = sign_dict(self.sk, header)
        block_id, height = self.store.commit_block(
            txs, signed_header["sig"], signed_header["pub"], header_hash, merkle, header["ts"]
        )
        return {
            "block_id": block_id,
            "height": height,
            "header_hash": header_hash,
            "txs": txs,
        }
