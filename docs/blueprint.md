# Whalez-AI Sovereign Stack Blueprint

The blueprint describes the high-level capabilities of the sovereign stack
included in this repository. It is intentionally concise so it can double as a
briefing for new contributors.

## Identity
- Deterministic identity file stored at `core/whalez_identity.json`.
- Append-only affirmation log maintained by `core/affirmation_core.py`.

## Agents
- `InterfaceAgent` exposes a public HTTP facade.
- `SelfHostingAgent` simulates DNS and deployment attestations.
- `SecurityAgent` monitors for abuse and writes defensive logs.
- Treasury, Ledger, Field and Governance agents provide minimal stubs for
  future automation.

## Virtual Machine
- `WhalezChainVM` maintains canonical state snapshots in `data/state.json` and
  persists block files under `ledger/`.
- `first_run.py` bootstraps the genesis blocks for development environments.

## Data Surfaces
- Affirmations, security incidents and deployment proofs are kept in
  human-readable JSONL files under the `data/` directory.
- Web interface assets live in `web/` and are served by the interface agent.

## Next Steps
1. Replace the placeholder identity hash with a verified value.
2. Feed production DNS and SSL proofs into the deployment manifest.
3. Extend the Treasury and Governance agents with real business logic.
