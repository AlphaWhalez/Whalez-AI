# Whalez-AI — Production Runbook (Stage 4)

## Windows (local prod)
1. Open **PowerShell as Administrator** in repo root.
2. One-time Python deps:

scripts\windows\setup_python.bat

3. Install service:

PowerShell -ExecutionPolicy Bypass -File scripts\windows\install_service.ps1

4. Start service immediately (first run):

scripts\windows\start_backend_service.bat

or reboot to let the Scheduled Task start it at boot.
5. Optional watchdog:

PowerShell -ExecutionPolicy Bypass -File scripts\windows\watchdog.ps1

## Linux (VPS)

chmod +x scripts/linux/start_backend_gunicorn.sh
PORT=5050 ./scripts/linux/start_backend_gunicorn.sh

## HTTPS
Set paths in `.env`: `TLS_CERT_PATH`, `TLS_KEY_PATH`.  
For local self-signed, use `scripts/windows/make_dev_cert.ps1` (already in repo from Stage 3).

## Logs & Telemetry
- API log: `logs/gateway.log`
- Telemetry/errors: `data/telemetry.jsonl`
- Commands: `data/command_log.jsonl`

## Health
- `GET /api/health` — green = online
- `GET /api/version` — shows deployed version
