@echo off
setlocal
cd /d "%~dp0..\..\web"
if not exist node_modules (
  echo [+] Installing web deps...
  npm install
)
echo [+] Starting web dev server on http://127.0.0.1:5173 ...
npm run dev

