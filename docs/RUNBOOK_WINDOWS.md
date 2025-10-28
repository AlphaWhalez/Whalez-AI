# Windows Runbook

## A. Backend

cd “C:\Users\Administrator\Documents\Dev\Whalez-AI”
scripts\windows\setup_python.bat
scripts\windows\start_backend.bat

Test:
- http://127.0.0.1:5050/api/ping
- http://127.0.0.1:5050/api/health

## B. Web

scripts\windows\start_web.bat

Open http://127.0.0.1:5173

## C. Mobile
- Edit `app/mobile/App.js` → set `BASE_URL` to your PC LAN IP with `:5050`

scripts\windows\start_mobile.bat

Scan QR in Expo Go (iOS/Android).

## D. Git Push

git add .
git commit -m “feat: initial Whalez-AI stack”
git branch -M main
git remote add origin https://github.com/AlphaWhalez/Whalez-AI.git
git push -u origin main

