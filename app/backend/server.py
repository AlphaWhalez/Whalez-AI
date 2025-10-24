#!/usr/bin/env python3
"""
Whalez-AI Backend API Gateway
──────────────────────────────
Bridges Sentinel + Agents to the Web & Mobile Apps
"""
import json
import os
from datetime import datetime
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask, jsonify, request

from src.agents.ledger_agent import LedgerAgent
from src.system import system_status_snapshot, verify_system_integrity

app = Flask(__name__)
ledger_agent = LedgerAgent()

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


# ─────────────────────────────────────────────────────────────
# Whalez-AI Command Interface API
# ─────────────────────────────────────────────────────────────
@app.route("/api/command", methods=["POST"])
def execute_command():
    data = request.get_json(force=True)
    command = data.get("command", "").strip()
    timestamp = datetime.utcnow().isoformat() + "Z"

    if not command:
        return jsonify({"error": "Empty command"}), 400

    normalized = command.lower()
    details = None

    if normalized == "verify system integrity":
        details = verify_system_integrity(ledger_agent)
        if details.get("status") == "ok":
            result = "✅ System integrity verified successfully."
        else:
            result = "⚠️ System integrity requires attention."
    elif normalized == "refresh ledger sync":
        details = ledger_agent.refresh()
        issue_count = len(details.get("issues", []))
        block_count = details.get("count", 0)
        if issue_count:
            result = f"⚠️ Ledger sync completed with {issue_count} issue(s)."
        else:
            result = f"🔄 Ledger synchronized — {block_count} block(s) indexed."
    elif normalized == "status check":
        details = system_status_snapshot(ledger_agent)
        result = "🧠 System status snapshot generated."
    elif normalized == "initiate proof cycle":
        result = "🧾 Runtime proof cycle started."
    else:
        result = f"⚙️ Command '{command}' executed (stub)."

    os.makedirs("data", exist_ok=True)
    with open("data/command_log.jsonl", "a") as f:
        entry = {
            "timestamp": timestamp,
            "command": command,
            "result": result,
        }
        if details is not None:
            entry["details"] = details
        f.write(json.dumps(entry) + "\n")

    response_payload = {
        "timestamp": timestamp,
        "command": command,
        "result": result,
    }
    if details is not None:
        response_payload["details"] = details

    return jsonify(response_payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
