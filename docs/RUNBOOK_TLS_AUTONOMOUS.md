# Whalez-Ai Autonomous TLS (WADA)

## What you get
- Hybrid TLS: Let’s Encrypt (future hook) + Self-CA fallback
- Auto-issue and rotate certs under `certs/live/<domain>/`
- Audit log at `logs/tls_audit.log`

## Quick start (Windows)
```bat
scripts\windows\start_secure.bat
```

Open: https://127.0.0.1:4443/api/ping
(You’ll see a browser warning for self-CA; accept/trust locally.)

## Quick start (Linux/macOS)
```bash
bash scripts/linux/start_secure.sh
```

## Change HTTPS port
Edit: `config/tls.settings.json` → `bind.https_port`

## Production notes
- Point DNS of your real domain to your server IP
- Set `WHALEZ_DOMAIN` env to that domain
- (Future) enable ACME issuance in `core/domain_authority/manager.py`

---

# 🧪 How to run (now)

**Windows Terminal**
```bat
cd "C:\\Users\\Administrator\\Documents\\Dev\\Whalez-AI"
scripts\windows\start_secure.bat
```

Open in browser (you’ll see a trust warning on first use due to self-CA):
- https://127.0.0.1:4443/api/ping
- https://127.0.0.1:4443/api/health

Your Expo mobile app should still talk to the backend on 5050 (HTTP) as before unless you switch it to HTTPS. If you want the mobile app to hit HTTPS, set `BASE_URL = "https://<your-lan-ip>:4443"` and accept the self-signed cert on device (or install the CA).

---

## 📦 Add deps once (if needed)

If Codex doesn’t auto-install:

```bat
cd "C:\\Users\\Administrator\\Documents\\Dev\\Whalez-AI"
venv\Scripts\activate
python -m pip install cryptography
```
