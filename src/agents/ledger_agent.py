"""Ledger agent primitives for Whalez-AI."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(order=True)
class LedgerBlock:
    """Dataclass representation of a Whalez ledger block."""

    number: int
    path: Path = field(compare=False)
    tx_type: str = field(compare=False)
    timestamp: str = field(compare=False)
    state_hash: str = field(compare=False)
    payload: Dict[str, object] = field(compare=False, default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serialisable representation of the block."""

        return {
            "number": self.number,
            "path": str(self.path),
            "tx_type": self.tx_type,
            "timestamp": self.timestamp,
            "state_hash": self.state_hash,
            "payload": self.payload,
        }


@dataclass
class LedgerAgent:
    """Utility class that tracks and validates ledger block files."""

    ledger_dir: Path = Path("ledger")
    blocks: List[LedgerBlock] = field(default_factory=list)
    _last_summary: Optional[Dict[str, object]] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self.ledger_dir = Path(self.ledger_dir)
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def register_block(self, block_path: Path) -> None:
        """Register a new block on disk, updating the in-memory index."""

        block = self._load_block(Path(block_path))
        self._upsert_block(block)
        self._last_summary = None

    def list_blocks(self) -> List[str]:
        """Return the currently indexed block paths in ledger order."""

        if not self.blocks:
            return []
        return [str(block.path) for block in sorted(self.blocks)]

    def latest_block(self) -> Optional[LedgerBlock]:
        """Return the most recent block or ``None`` when empty."""

        if not self.blocks:
            return None
        return max(self.blocks)

    def refresh(self) -> Dict[str, object]:
        """Re-scan the ledger directory and return a summary."""

        issues: List[str] = []
        blocks: List[LedgerBlock] = []
        seen_numbers: set[int] = set()

        for path in sorted(self.ledger_dir.glob("block_*.whlzblk")):
            try:
                block = self._load_block(path)
            except ValueError as exc:
                issues.append(f"{path.name}: {exc}")
                continue
            if block.number in seen_numbers:
                issues.append(f"duplicate block number detected: {block.number}")
                continue
            seen_numbers.add(block.number)
            blocks.append(block)

        blocks.sort()
        sequence_issues = self._detect_sequence_anomalies(blocks)
        issues.extend(sequence_issues)

        self.blocks = blocks
        summary = self._build_summary(issues)
        self._last_summary = summary
        return summary

    def summary(self) -> Dict[str, object]:
        """Return the last refresh summary, re-indexing if necessary."""

        if self._last_summary is None:
            return self.refresh()
        return self._last_summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_block(self, path: Path) -> LedgerBlock:
        """Parse a block file into a :class:`LedgerBlock`."""

        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError("block file missing") from exc
        except json.JSONDecodeError as exc:
            raise ValueError("invalid JSON payload") from exc

        number = payload.get("number")
        tx_type = payload.get("tx_type")
        timestamp = payload.get("timestamp")
        state_hash = payload.get("state_hash")

        if not isinstance(number, int):
            raise ValueError("block missing integer 'number'")
        if not isinstance(tx_type, str):
            raise ValueError("block missing string 'tx_type'")
        if not isinstance(timestamp, str):
            raise ValueError("block missing string 'timestamp'")
        if not isinstance(state_hash, str):
            raise ValueError("block missing string 'state_hash'")

        payload_field = payload.get("payload")
        payload_dict: Dict[str, object]
        if isinstance(payload_field, dict):
            payload_dict = payload_field
        else:
            payload_dict = {}

        return LedgerBlock(
            number=number,
            path=Path(path),
            tx_type=tx_type,
            timestamp=timestamp,
            state_hash=state_hash,
            payload=payload_dict,
        )

    def _detect_sequence_anomalies(self, blocks: List[LedgerBlock]) -> List[str]:
        issues: List[str] = []
        expected = 1
        for block in blocks:
            if block.number != expected:
                if block.number < expected:
                    issues.append(
                        f"unexpected block ordering: found {block.number}, expected >= {expected}"
                    )
                else:
                    issues.append(
                        f"gap detected before block {block.number}: expected block {expected}"
                    )
                    expected = block.number
            expected = block.number + 1
        return issues

    def _build_summary(self, issues: List[str]) -> Dict[str, object]:
        latest = self.latest_block()
        return {
            "count": len(self.blocks),
            "latest": latest.to_dict() if latest else None,
            "expected_next": (latest.number + 1) if latest else 1,
            "issues": issues,
            "paths": [str(block.path) for block in self.blocks],
        }

    def _upsert_block(self, block: LedgerBlock) -> None:
        self.blocks = [b for b in self.blocks if b.number != block.number]
        self.blocks.append(block)
        self.blocks.sort()


__all__ = ["LedgerAgent", "LedgerBlock"]
