# Self-Hosting Guide

This document walks through the process of launching the Whalez sovereign stack
on self-managed infrastructure.

## 1. Prepare Environment
1. Create a Python 3.11 virtual environment.
2. Install dependencies using `pip install -r requirements.txt`.
3. Update `core/whalez_identity.json` with your real founder hash and fingerprint.

## 2. Generate Proofs
1. Run `python -m src.vm.first_run` to seal the genesis blocks.
2. Inspect the resulting files in `ledger/` and `data/first_run_summary.json`.
3. Replace placeholders in `data/domain_proof_manifest.json` with production
   DNS and SSL evidence.

## 3. Operate the Interface
1. Start the orchestrator with `python run_whalez.py`.
2. Point your reverse proxy to the port configured in `run_whalez.py` (default `8080`).
3. Feed request metadata into `SecurityAgent.record_request` to enable rate
   limiting and blocklist generation.

## 4. Maintain the Ledger
- The WhalezChain VM writes append-only block files. Back up the `ledger/`
  directory regularly.
- Extend `TreasuryAgent` and `GovernanceAgent` as you introduce real economic
  logic.

## 5. Monitoring
- Review `data/security_incidents.jsonl` for suspicious activity.
- Affirmations in `data/affirmations.jsonl` provide an auditable change log.
