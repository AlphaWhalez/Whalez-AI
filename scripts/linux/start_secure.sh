#!/usr/bin/env bash
set -euo pipefail
python - <<'PY'
from core.tls_engine.bootstrap import ensure_tls_artifacts
print(ensure_tls_artifacts())
PY
echo "TLS artifacts ready."
# Hook: start your HTTPS gateway here (uvicorn/traefik/nginx as you prefer)
