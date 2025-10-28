# Stage 2 — Production-leaning Setup (Windows)

## Start backend (port 5050)

```
cd "C:\\Users\\Administrator\\Documents\\Dev\\Whalez-AI"
scripts\windows\start_backend.bat
```

Test:
- http://127.0.0.1:5050/api/ping
- http://127.0.0.1:5050/api/health
- http://127.0.0.1:5050/api/registry
- POST http://127.0.0.1:5050/api/payroll/preview  body: {"total_pltr":100}

## Optional reverse proxy (port 80 → 5050)

```
choco install caddy -y   (if not installed)
scripts\windows\start_proxy.bat
```

Then open http://localhost/

## Mobile app

```
cd "C:\\Users\\Administrator\\Documents\\Dev\\Whalez-AI\\app\\mobile"
npm install
npx expo start --tunnel
```

Set `BASE_URL` inside App.js to your LAN IPv4: `http://<your-ip>:5050`.

## Git push (if needed)

```
git add .
git commit -m "feat(stage2): registry + legacy-safe core, hardened API, Windows proxy"
git push -u origin main
```
