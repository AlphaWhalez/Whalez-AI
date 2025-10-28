# Architecture

## Layers
1. **API Gateway (Flask)** — `/api/*`: health, agents, command, payroll.
2. **Agents**
   - `LedgerAgent`: append-only ledger index, integrity checks.
3. **Payroll Engine**
   - Weighted allocation → proof emission `data/reward_proofs.jsonl`.
4. **Web SPA (Vite/React)** — Read-only console for ops.
5. **Mobile (Expo)** — Mirror health + simple status for on-the-go.

## Ports
- Backend: **5050**
- Web dev: 5173
- Expo bundler: 8081 (bundler only; backend still 5050)

## Security posture (baseline)
- Local development only; secrets via `.env` (do not commit real secrets).
- Firewall allowlist for Python/Node if testing across devices.

