@echo off
setlocal
cd /d "%~dp0..\..\"
echo [+] Working dir: %CD%

where caddy >NUL 2>&1
if errorlevel 1 (
  echo [!] Caddy not found. Install via Chocolatey:
  echo     choco install caddy -y
  echo Or download binary from caddyserver.com
  exit /b 1
)

if not exist logs mkdir logs
echo [+] Launching Caddy on :80 -> 127.0.0.1:5050 ...
caddy run --config scripts\windows\Caddyfile
