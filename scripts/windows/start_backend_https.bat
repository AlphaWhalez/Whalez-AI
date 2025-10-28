@echo off
setlocal
cd /d "%~dp0..\..\"
echo [+] Working dir: %CD%

if not exist venv (
  echo [+] Creating venv...
  py -3 -m venv venv
)
call venv\Scripts\activate

echo [+] Installing Python deps...
python -m pip install --upgrade pip wheel
python -m pip install flask python-dotenv psutil

set PYTHONPATH=%CD%
if not exist certs (
  echo [!] No certs/ directory. Run: powershell -ExecutionPolicy Bypass -File scripts\windows\make_dev_cert.ps1
  goto :eof
)

if not exist .env (
  echo PORT=5050> .env
  echo BIND_HOST=0.0.0.0>> .env
  echo CORS_ALLOW=*>> .env
  echo SSL_CERT=certs/cert.pem>> .env
  echo SSL_KEY=certs/key.pem>> .env
  echo [+] Created .env with HTTPS settings.
)

for /f "usebackq tokens=1,2 delims==" %%a in (".env") do set %%a=%%b
echo [+] PYTHONPATH=%PYTHONPATH%
echo [+] Starting backend on HTTPS %BIND_HOST%:%PORT% ...
python api\gateway.py
