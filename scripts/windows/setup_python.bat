@echo off
setlocal
cd /d "%~dp0..\..\"
if not exist venv (
  echo [+] Creating Python venv...
  py -3 -m venv venv
)
call venv\Scripts\activate
python -m pip install --upgrade pip wheel
python -m pip install flask python-dotenv psutil
echo [+] Python ready.

