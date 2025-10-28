@echo off
setlocal
cd /d "%~dp0..\..\app\mobile"
if not exist node_modules (
  echo [+] Installing mobile deps...
  npm install
)
echo [+] Starting Expo (tunnel)...
npx expo start --tunnel

