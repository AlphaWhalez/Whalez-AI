@echo off
python - <<PY
from core.tls_engine.bootstrap import ensure_tls_artifacts
print(ensure_tls_artifacts())
PY
echo TLS artifacts ready.
