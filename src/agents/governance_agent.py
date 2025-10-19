"""Governance agent stub for Whalez-AI."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class GovernanceAgent:
    """Minimal governance proposal tracker."""

    proposals: List[Dict[str, str]] = field(default_factory=list)

    def submit(self, title: str, description: str) -> Dict[str, str]:
        proposal = {"title": title, "description": description}
        self.proposals.append(proposal)
        return proposal

    def list_proposals(self) -> List[Dict[str, str]]:
        return list(self.proposals)


__all__ = ["GovernanceAgent"]
