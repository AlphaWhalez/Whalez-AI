#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/.."

export PYTHONPATH="$PWD"

LOOP_INTERVAL="${GOVERNANCE_LOOP_INTERVAL:-30}"
EXECUTE_FLAG=""
if [[ "${GOVERNANCE_EXECUTE:-0}" == "1" ]]; then
  EXECUTE_FLAG="--execute"
fi

python -m core.controllers.orchestrator --loop "$LOOP_INTERVAL" $EXECUTE_FLAG "$@"
