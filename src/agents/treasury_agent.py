"""Treasury agent stub for Whalez-AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TreasuryAgent:
    """Minimal treasury agent placeholder."""

    balances: Dict[str, int] = field(default_factory=dict)

    def credit(self, account: str, amount: int) -> None:
        self.balances[account] = self.balances.get(account, 0) + amount

    def snapshot(self) -> Dict[str, int]:
        return dict(self.balances)


__all__ = ["TreasuryAgent"]
