@echo off
setlocal
cd /d "%~dp0..\..\"
call venv\Scripts\activate
if exist .env (
  for /f "usebackq tokens=1,* delims==" %%a in (".env") do set %%a=%%b
)
if "%PORT%"=="" set PORT=5050
if "%BIND_HOST%"=="" set BIND_HOST=0.0.0.0
echo [+] Starting backend on %BIND_HOST%:%PORT% ...
python api\gateway.py

