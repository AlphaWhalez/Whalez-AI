"""Minimal Whalezchain virtual machine implementation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any
from datetime import datetime, timezone


class TransactionError(RuntimeError):
    """Raised when a transaction cannot be applied."""


@dataclass
class WhalezChainVM:
    """Simplified state manager for the Whalez ledger."""

    ledger_dir: Path = Path("ledger")
    state_path: Path = Path("data/state.json")
    state: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        if self.state_path.exists():
            try:
                self.state = json.loads(self.state_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.state = {}
        self.state.setdefault("ownership_proof", None)
        self.state.setdefault("treasury", {})
        self.state.setdefault("snapshots", [])

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2, sort_keys=True), encoding="utf-8")

    def apply_transaction(self, tx_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if tx_type == "OWNERSHIP_PROOF":
            proof = payload.get("proof")
            if not proof:
                raise TransactionError("OWNERSHIP_PROOF requires 'proof'")
            self.state["ownership_proof"] = {
                "proof": proof,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        elif tx_type == "TREASURY_INIT":
            initial_balance = payload.get("initial_balance")
            if not isinstance(initial_balance, (int, float)):
                raise TransactionError("TREASURY_INIT requires numeric 'initial_balance'")
            self.state["treasury"]["reserve"] = float(initial_balance)
        elif tx_type == "SNAPSHOT_REF":
            ref = payload.get("reference")
            if not ref:
                raise TransactionError("SNAPSHOT_REF requires 'reference'")
            self.state["snapshots"].append({
                "reference": ref,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        else:
            raise TransactionError(f"Unknown transaction type {tx_type}")

        self._save_state()
        return self.write_block(tx_type, payload)

    def _next_block_number(self) -> int:
        existing = list(self.ledger_dir.glob("block_*.whlzblk"))
        highest = 0
        for path in existing:
            try:
                number = int(path.stem.split("_")[1])
                highest = max(highest, number)
            except (IndexError, ValueError):
                continue
        return highest + 1

    def write_block(self, tx_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        block_number = self._next_block_number()
        block = {
            "number": block_number,
            "tx_type": tx_type,
            "payload": payload,
            "state_hash": self._state_hash(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        block_path = self.ledger_dir / f"block_{block_number}.whlzblk"
        block_path.write_text(json.dumps(block, indent=2, sort_keys=True), encoding="utf-8")
        return {"path": str(block_path), "block": block}

    def _state_hash(self) -> str:
        serialized = json.dumps(self.state, sort_keys=True).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()


__all__ = ["WhalezChainVM", "TransactionError"]
