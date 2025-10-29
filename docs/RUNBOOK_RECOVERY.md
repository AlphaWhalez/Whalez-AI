# Recovery & Self-Heal Runbook

## What it does
- Runs health probes (imports, toolchain presence, gateway compile).
- Records last-known state in `.whalez/state.json`.
- If any probe fails, executes platform restart hook:
  - Linux: `scripts/linux/start_orchestrator.sh`
  - Windows: `scripts/windows/start_orchestrator.bat`

## Operator actions
- **Status**: `GET /recovery/status` (scope: `ops:read`)
- **Reconcile**: `POST /recovery/reconcile` (scope: `ops:write`)

## Environment
- `STATE_SNAPSHOT_PATH` (optional): override snapshot path.
- `SERVICE_RESTART_CMD`, `SERVICE_RESTART_WIN` (optional): custom restart commands.

## CI
- Job **Self-heal preflight** runs `scripts/ci/preflight_self_heal.py`. Build fails if any Python exception occurs.
