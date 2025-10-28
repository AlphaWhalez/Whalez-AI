@echo off
setlocal
cd /d "%~dp0..\..\web"
echo [+] Working dir: %CD%

if not exist node_modules (
  echo [+] Installing web deps...
  call npm install
)

set VITE_BACKEND=http://127.0.0.1:5050
echo [+] Starting web dashboard on http://127.0.0.1:5173 ...
call npm run dev
