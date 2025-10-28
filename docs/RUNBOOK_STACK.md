# Whalez-AI Stack Runbook (Stage 5)

## Local / Windows VPS
1. Set environment (optional):
   - `set PORT=5050`
   - `set WEB_PORT=5173`
   - `set ENABLE_HTTPS=true` and provide `SSL_CERT_PATH`, `SSL_KEY_PATH` if you want HTTPS.
2. Start everything:

scripts\windows\start_stack.bat

3. Verify:
- API: http://127.0.0.1:5050/api/health
- Web: http://localhost:5173
4. Stop:

scripts\windows\stop_stack.bat

## CI Artifacts
Every push builds `web/dist` and publishes an artifact named **web-dist**.
