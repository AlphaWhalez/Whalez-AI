@echo off
setlocal
cd /d "%~dp0..\..\"
if not defined PYTHONPATH set PYTHONPATH=%CD%
call venv\Scripts\activate
REM Use Waitress WSGI server for Windows
python -m pip install --disable-pip-version-check waitress
echo [+] Launching Waitress on port %PORT% (or SERVICE_PORT) ...
if "%PORT%"=="" set PORT=%SERVICE_PORT%
if "%PORT%"=="" set PORT=5050
waitress-serve --listen=0.0.0.0:%PORT% api.gateway:app
