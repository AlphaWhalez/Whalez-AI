#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD:${PYTHONPATH:-}"
python3 -m venv venv || true
source venv/bin/activate
pip install --upgrade pip wheel gunicorn
exec gunicorn -w 2 -b 0.0.0.0:${PORT:-5050} api.gateway:app
