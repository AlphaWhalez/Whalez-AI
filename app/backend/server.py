#!/usr/bin/env python3
"""
Whalez-AI Backend API Gateway
──────────────────────────────
Bridges Sentinel + Agents to the Web & Mobile Apps
"""
from flask import Flask, jsonify
import json, os
from datetime import datetime
import random

app = Flask(__name__)

@app.route("/api/health")
def get_health():
    path = "data/runtime_proofs.jsonl"
    if not os.path.exists(path):
        return jsonify({"error": "No runtime logs yet"}), 404
    with open(path) as f:
        lines = f.readlines()[-10:]
    return jsonify({"recent_logs": [json.loads(l) for l in lines]})

@app.route("/api/ping")
def ping():
    return jsonify({"status": "Whalez-AI App Gateway online ✅"})


# ─────────────────────────────────────────────────────────────
# Whalez-AI Agent Activity API
# ─────────────────────────────────────────────────────────────
@app.route("/api/agents/status")
def get_agents_status():
    agents = [
        {
            "name": "InterfaceAgent",
            "module": "interface_agent.py",
            "status": random.choice(["active", "idle", "error"]),
            "last_heartbeat": datetime.utcnow().isoformat() + "Z",
            "task": random.choice([
                "Processing user intent",
                "Rendering UI response",
                "Idle — waiting for request",
                "Syncing with LedgerAgent",
            ]),
        },
        {
            "name": "LedgerAgent",
            "module": "ledger_agent.py",
            "status": random.choice(["active", "idle", "error"]),
            "last_heartbeat": datetime.utcnow().isoformat() + "Z",
            "task": random.choice([
                "Updating ledger entries",
                "Validating transaction proofs",
                "Idle — standby",
                "Integrity scan",
            ]),
        },
        {
            "name": "GovernanceAgent",
            "module": "governance_agent.py",
            "status": random.choice(["active", "idle", "error"]),
            "last_heartbeat": datetime.utcnow().isoformat() + "Z",
            "task": random.choice([
                "Policy evaluation",
                "Idle — standby",
                "Consensus alignment",
                "System check",
            ]),
        },
    ]
    return jsonify({"agents": agents})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
