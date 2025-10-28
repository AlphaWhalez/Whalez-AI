@echo off
setlocal
cd /d "%~dp0..\..\app\mobile"
echo [+] Mobile dir: %CD%
if not exist node_modules (
  echo [+] Installing deps...
  npm install
)
echo [+] Starting Expo (tunnel)...
npx expo start --tunnel
