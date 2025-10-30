from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Any, Dict, List, Optional

_DEFAULT_LEDGER_PATH = "data/intent_ledger.sqlite3"


class IntentNotFound(Exception):
    """Raised when an intent record is not present in the ledger."""


class IntentLedger:
    def __init__(self, path: str | None = None) -> None:
        ledger_path = path or os.getenv("INTENT_LEDGER_PATH", _DEFAULT_LEDGER_PATH)
        directory = os.path.dirname(ledger_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        self.path = ledger_path
        self._init()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path, timeout=10, isolation_level=None)

    def _init(self) -> None:
        with self._conn() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS intents (
                  id TEXT PRIMARY KEY,
                  kind TEXT,
                  status TEXT,
                  payload TEXT,
                  result TEXT,
                  created_at REAL,
                  updated_at REAL
                )
                """
            )

    def upsert(
        self,
        *,
        id: str,
        kind: str,
        status: str,
        payload: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = time.time()
        row = (
            id,
            kind,
            status,
            json.dumps(payload) if payload is not None else None,
            json.dumps(result) if result is not None else None,
            now,
            now,
        )
        with self._conn() as connection:
            connection.execute(
                """
                INSERT INTO intents(id,kind,status,payload,result,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                  kind=excluded.kind,
                  status=excluded.status,
                  payload=excluded.payload,
                  result=excluded.result,
                  updated_at=excluded.updated_at
                """,
                row,
            )

    def get(self, id: str) -> Dict[str, Any]:
        with self._conn() as connection:
            cursor = connection.execute(
                "SELECT id,kind,status,payload,result,created_at,updated_at FROM intents WHERE id=?",
                (id,),
            )
            record = cursor.fetchone()
        if not record:
            raise IntentNotFound(id)
        payload = json.loads(record[3]) if record[3] else {}
        result = json.loads(record[4]) if record[4] else None
        return {
            "id": record[0],
            "kind": record[1],
            "status": record[2],
            "payload": payload,
            "result": result,
            "created_at": record[5],
            "updated_at": record[6],
        }

    def list(
        self,
        *,
        limit: int = 100,
        kind: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = "SELECT id,kind,status,payload,result,created_at,updated_at FROM intents"
        conditions: List[str] = []
        args: List[Any] = []
        if kind:
            conditions.append("kind=?")
            args.append(kind)
        if status:
            conditions.append("status=?")
            args.append(status)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY updated_at DESC LIMIT ?"
        args.append(limit)
        with self._conn() as connection:
            rows = connection.execute(query, args).fetchall()
        output: List[Dict[str, Any]] = []
        for row in rows:
            output.append(
                {
                    "id": row[0],
                    "kind": row[1],
                    "status": row[2],
                    "payload": json.loads(row[3]) if row[3] else {},
                    "result": json.loads(row[4]) if row[4] else None,
                    "created_at": row[5],
                    "updated_at": row[6],
                }
            )
        return output
