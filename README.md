# Whalez-AI Sovereign Stack v1.1

The Whalez-AI Sovereign Stack is a self-governing orchestration layer that
combines deterministic identity, defensive telemetry and a minimal ledger. This
repository contains a development-friendly distribution of the stack with
stubs for future financial and governance automation.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
python run_whalez.py
```

Visit [http://localhost:8080](http://localhost:8080) to view the interface.

## First Run Sealing (Optional)

```bash
python -m src.vm.first_run
```

This command initializes development genesis blocks:

- `ledger/block_1.whlzblk` containing the `OWNERSHIP_PROOF` transaction.
- `ledger/block_2.whlzblk` containing the `TREASURY_INIT` transaction.

## Repository Layout

| Path | Description |
| --- | --- |
| `core/` | Identity configuration, affirmation logging and deterministic subdomain utilities. |
| `src/agents/` | Interface, self-hosting, security and future agent stubs. |
| `src/vm/` | Minimal Whalezchain VM and `first_run.py` helper. |
| `web/` | Frontend scaffold served by the interface agent. |
| `docs/` | Blueprint, architecture notes and self-hosting guide. |
| `data/` | Append-only runtime logs and manifests. |
| `ledger/` | Block files produced by the Whalezchain VM. |

## Next Steps

1. Replace placeholder identity values in `core/whalez_identity.json`.
2. Connect the self-hosting agent to your infrastructure proofs.
3. Integrate the `SecurityAgent` with your API layer to feed request events.
