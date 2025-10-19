"""First-run sealing flow for the Whalezchain VM."""

from __future__ import annotations

import json
from pathlib import Path

from core.affirmation_core import AffirmationCore
from core.self_domain import deterministic_subdomain
from ..agents.self_hosting_agent import SelfHostingAgent
from .whalez_vm import WhalezChainVM


def seal_genesis(identity_path: Path | str = Path("core/whalez_identity.json")) -> None:
    core = AffirmationCore(identity_path)
    vm = WhalezChainVM()
    agent = SelfHostingAgent()

    subdomain = deterministic_subdomain(core.identity)
    core.append("Bootstrapping Whalezchain VM", {"subdomain": subdomain})

    block1 = vm.apply_transaction(
        "OWNERSHIP_PROOF",
        {
            "proof": core.identity.public_key_fingerprint,
            "domain": subdomain,
        },
    )

    block2 = vm.apply_transaction(
        "TREASURY_INIT",
        {
            "initial_balance": 0.0,
            "currency": "WHALEZ",
        },
    )

    agent.record_deployment("local-dev", subdomain, note="first_run bootstrap")

    summary = {
        "ownership_block": block1["path"],
        "treasury_block": block2["path"],
        "subdomain": subdomain,
    }
    (Path("data") / "first_run_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("Genesis sealing complete:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    seal_genesis()
