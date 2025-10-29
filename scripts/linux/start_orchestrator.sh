#!/usr/bin/env bash
set -euo pipefail
python -m pip install -r requirements.txt || true
uvicorn api.gateway:app --host 0.0.0.0 --port 5000
