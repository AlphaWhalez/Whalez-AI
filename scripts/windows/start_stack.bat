@echo off
setlocal enabledelayedexpansion
cd /d %~dp0\..\..
echo [*] Whalez-AI Stage 5: start full stack

REM --- Environment defaults ---
if not defined PORT set PORT=5050
if not defined WEB_PORT set WEB_PORT=5173
if not defined ENABLE_HTTPS set ENABLE_HTTPS=false

echo [*] Working dir: %CD%
echo [*] API port: %PORT%  WEB port: %WEB_PORT%  HTTPS: %ENABLE_HTTPS%

REM --- Start backend (HTTPS if enabled) ---
if /I "%ENABLE_HTTPS%"=="true" (
  echo [+] Starting backend (HTTPS)...
  start "whalez-backend-https" cmd /c scripts\windows\start_backend_https.bat
) else (
  echo [+] Starting backend (HTTP)...
  start "whalez-backend" cmd /c scripts\windows\start_backend.bat
)

REM --- Start web preview (Vite preview over built dist) ---
echo [+] Building web...
cd web && npm install --no-audit --no-fund && npm run build && cd ..
echo [+] Launching web preview on http://localhost:%WEB_PORT% ...
start "whalez-web" cmd /c npm --prefix web run preview -- --port %WEB_PORT% --strictPort

REM --- Health checks ---
echo [+] Waiting for services...
powershell -NoLogo -NoProfile -Command ^
  "$ErrorActionPreference='SilentlyContinue';" ^
  "for($i=0;$i -lt 30;$i++){"
  "$h=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:%PORT%/api/health -TimeoutSec 2; if($h.StatusCode -eq 200){'API healthy ✅'; exit 0}; Start-Sleep -Seconds 1}"
  "exit 1"
if errorlevel 1 ( echo [!] API not responding & goto :end )

echo [+] Opening dashboards...
start http://127.0.0.1:%PORT%/api/health
start http://localhost:%WEB_PORT%/

:end
echo [*] Stack started. Press Ctrl+C in individual windows to stop.
endlocal
