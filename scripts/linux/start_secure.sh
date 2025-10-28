#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."

python3 -m venv venv || true
source venv/bin/activate

pip install --upgrade pip wheel
pip install flask python-dotenv psutil cryptography

export WHALEZ_DOMAIN="whalez-ai.local"
export WHALEZ_DOMAIN_HOST="127.0.0.1"

mkdir -p logs certs
python core/tls_engine/bootstrap.py
