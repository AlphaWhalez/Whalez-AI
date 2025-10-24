"""Operational diagnostics helpers for Whalez-AI."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.affirmation_core import AffirmationCore
from core.self_domain import deterministic_subdomain
from src.agents.ledger_agent import LedgerAgent
from src.vm.whalez_vm import WhalezChainVM


def verify_system_integrity(ledger_agent: Optional[LedgerAgent] = None) -> Dict[str, Any]:
    """Return a diagnostic report for core ledger and state assets."""

    agent = ledger_agent or LedgerAgent()
    ledger_summary = agent.refresh()

    vm = WhalezChainVM()
    state_hash = vm.current_state_hash()

    core = AffirmationCore()
    latest_affirmation = core.latest()

    issues = list(ledger_summary.get("issues", []))
    latest_block = agent.latest_block()
    if latest_block and latest_block.state_hash != state_hash:
        issues.append("state hash mismatch between VM snapshot and latest block")

    return {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok" if not issues else "degraded",
        "identity": {
            "name": core.identity.identity_name,
            "subdomain": deterministic_subdomain(core.identity),
        },
        "ledger": ledger_summary,
        "state": {
            "path": str(vm.state_path),
            "hash": state_hash,
        },
        "latest_affirmation": latest_affirmation,
        "issues": issues,
    }


def system_status_snapshot(ledger_agent: Optional[LedgerAgent] = None) -> Dict[str, Any]:
    """Return a high-level snapshot of system and ledger activity."""

    agent = ledger_agent or LedgerAgent()
    ledger_summary = agent.refresh()

    vm = WhalezChainVM()
    core = AffirmationCore()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "identity": {
            "name": core.identity.identity_name,
            "subdomain": deterministic_subdomain(core.identity),
        },
        "ledger": ledger_summary,
        "state": {
            "path": str(vm.state_path),
            "hash": vm.current_state_hash(),
        },
        "latest_affirmation": core.latest(),
    }


__all__ = ["verify_system_integrity", "system_status_snapshot"]
