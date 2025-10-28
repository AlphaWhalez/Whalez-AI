@echo off
setlocal

REM Move to repo root
cd /d "%~dp0..\..\"
echo [+] Working dir: %CD%

REM Python venv
if not exist venv (
  echo [+] Creating venv...
  py -3 -m venv venv
)
call venv\Scripts\activate

REM Deps (adds cryptography for self-CA)
echo [+] Installing Python deps...
python -m pip install --upgrade pip wheel
python -m pip install flask python-dotenv psutil cryptography

REM Env defaults
if not exist logs mkdir logs
if not exist certs mkdir certs
set WHALEZ_DOMAIN=whalez-ai.local
set WHALEZ_DOMAIN_HOST=127.0.0.1

REM Start secure HTTPS (self-CA or hybrid)
echo [+] Launching Whalez-AI secure gateway ...
python core\tls_engine\bootstrap.py
