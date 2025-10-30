"""Phase-M telemetry integration and console extension service."""

from __future__ import annotations

import logging
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import FastAPI, Request

# --- Initialization ---

# Ensure runtime imports resolve relative to the repository root.
sys.path.append(os.getcwd())

# Guarantee that the logs directory exists before configuring handlers.
os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("whalez_ai.telemetry")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("logs/telemetry.log", mode="a", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

app = FastAPI(title="Whalez-AI Telemetry Gateway")


# --- Core Telemetry Functions ---


def collect_system_metrics() -> Dict[str, Any]:
    """Capture system-level runtime metrics for the dashboard."""
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()._asdict()
    uptime = time.time() - psutil.boot_time()
    return {
        "cpu_percent": cpu,
        "memory": {
            "used": memory["used"],
            "available": memory["available"],
            "percent": memory["percent"],
        },
        "uptime_seconds": int(uptime),
    }


def collect_intent_trace(request: Request) -> Dict[str, Any]:
    """Capture simplified user-intent traces for autobiographical memory."""
    return {
        "method": request.method,
        "path": str(request.url.path),
        "timestamp": datetime.utcnow().isoformat(),
        "headers": dict(request.headers),
    }


# --- Routes ---


@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    """Middleware captures telemetry and intent traces on every request."""
    metrics = collect_system_metrics()
    trace = collect_intent_trace(request)
    logger.info("TRACE | %s %s | metrics=%s", trace["method"], trace["path"], metrics)
    response = await call_next(request)
    return response


@app.get("/telemetry/ping")
async def ping():
    """Simple test endpoint to verify telemetry system is live."""
    metrics = collect_system_metrics()
    logger.info("PING | Telemetry active | %s", metrics)
    return {"status": "ok", "metrics": metrics}


@app.get("/telemetry/logs")
async def get_logs():
    """Expose the last 100 log lines for the console dashboard."""
    try:
        with open("logs/telemetry.log", "r", encoding="utf-8") as f:
            lines = f.readlines()[-100:]
    except FileNotFoundError:
        return {"logs": []}
    return {"logs": [line.strip() for line in lines]}


# --- Launch Command ---
# To run locally or via CI/CD:
# export PYTHONPATH=$(pwd)
# uvicorn whalez_ai.telemetry:app --reload

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
