# HTTPS & CI

## Local HTTPS (dev)
1. Open **Windows PowerShell** in repo root:

powershell -ExecutionPolicy Bypass -File scripts/windows/make_dev_cert.ps1

2. This creates `certs/cert.pem` + `certs/key.pem` and writes suggested `.env` keys.
3. Start HTTPS server:

scripts\windows\start_backend_https.bat

Visit https://127.0.0.1:5050/api/ping (accept the self-signed warning).

## Web Dashboard

scripts\windows\start_web.bat

Open http://127.0.0.1:5173 — the dashboard proxies **/api** to backend:5050.

## CI
GitHub Actions builds backend imports and web build on every push/PR to `main`.
