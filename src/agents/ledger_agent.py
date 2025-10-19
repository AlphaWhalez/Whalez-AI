"""Ledger agent stub for Whalez-AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class LedgerAgent:
    """Placeholder ledger agent that tracks block file paths."""

    ledger_dir: Path = Path("ledger")
    blocks: List[Path] = field(default_factory=list)

    def register_block(self, block_path: Path) -> None:
        self.blocks.append(block_path)

    def list_blocks(self) -> List[str]:
        return [str(block) for block in self.blocks]


__all__ = ["LedgerAgent"]
