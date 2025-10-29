@echo off
python -m pip install -r requirements.txt
uvicorn api.gateway:app --host 0.0.0.0 --port 5000
