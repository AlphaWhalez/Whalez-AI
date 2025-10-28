@echo off
setlocal
cd /d "%~dp0..\..\"
echo [+] Working dir: %CD%

if not defined PYTHONPATH set PYTHONPATH=%CD%
echo [+] PYTHONPATH set to: %PYTHONPATH%

if not exist venv (
  echo [+] Creating venv...
  py -3 -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip wheel >NUL
python -m pip install flask python-dotenv psutil >NUL

call scripts\windows\print_ip.bat

if exist .env (
  for /f "usebackq tokens=1,* delims==" %%a in (".env") do set %%a=%%b
)
if "%PORT%"=="" set PORT=5050
if "%BIND_HOST%"=="" set BIND_HOST=0.0.0.0
if "%EXTERNAL_URL%"=="" set EXTERNAL_URL=http://127.0.0.1:%PORT%

echo [+] Starting backend on %BIND_HOST%:%PORT% (%EXTERNAL_URL%) ...
python api\gateway.py
