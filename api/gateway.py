#!/usr/bin/env python3
import os, json, random
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv

from src.agents.ledger_agent import LedgerAgent
from src.system import system_status_snapshot, verify_system_integrity
from src.payroll.engine import preview_allocation, payout

# Load env
load_dotenv()
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5050"))
CORS_ALLOW = os.getenv("CORS_ALLOW", "*")

def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = CORS_ALLOW
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

app = Flask(__name__)
ledger = LedgerAgent()

@app.after_request
def after(resp):
    return _cors(resp)

@app.route("/")
def root():
    return "<h2>🐋 Whalez-AI Gateway</h2><p>See /api/ping, /api/health, /api/agents/status, /api/payroll/preview</p>"

@app.route("/api/ping")
def ping():
    return jsonify({"status": "Whalez-AI online ✅", "port": PORT})

@app.route("/api/health")
def health():
    snap = system_status_snapshot(ledger)
    return jsonify({"status": "online", "metrics": snap})

@app.route("/api/agents/status")
def agents_status():
    agents = [
        {"name": "InterfaceAgent", "status": random.choice(["active","idle","error"]),
         "last_heartbeat": datetime.utcnow().isoformat()+"Z",
         "task": random.choice(["Processing intent","Rendering","Idle","Syncing ledger"])},
        {"name": "LedgerAgent", "status": "active", "last_heartbeat": datetime.utcnow().isoformat()+"Z",
         "task": "Indexing blocks", "count": ledger.count_blocks()}
    ]
    return jsonify({"agents": agents})

@app.route("/api/coach-model")
def coach_model():
    model = {
        "head_coaches": [{"id":"coach:tara_davis","role":"Head Coach Finance"}],
        "ai_coaches": {
            "BASIC": ["aicoach:basic_1","aicoach:basic_2","aicoach:basic_3"],
            "PRO":   ["aicoach:pro_1","aicoach:pro_2","aicoach:pro_3"],
            "VIP":   ["aicoach:vip_1","aicoach:vip_2","aicoach:vip_3"]
        },
        "vip_users": [{
            "id":"vip:james_head","display_name":"James Head","type":"public_investor",
            "sponsor":"coach:tara_davis","account_level":"VIP","status":"active_waiting_withdrawal"
        }]
    }
    return jsonify(model)

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json(force=True)
    cmd = (data.get("command") or "").strip().lower()
    ts = datetime.utcnow().isoformat()+"Z"
    if not cmd:
        return jsonify({"error": "Empty command"}), 400

    if cmd == "verify system integrity":
        details = verify_system_integrity(ledger)
        msg = "✅ System integrity verified." if details.get("status")=="ok" else "⚠️ Attention required."
    elif cmd == "refresh ledger sync":
        details = ledger.refresh()
        msg = f"🔄 Ledger synchronized — {details.get('count',0)} block(s)."
    else:
        details = {}
        msg = f"⚙️ Command '{cmd}' executed (stub)."

    os.makedirs("data", exist_ok=True)
    with open("data/command_log.jsonl","a") as f:
        f.write(json.dumps({"ts": ts, "command": cmd, "result": msg, "details": details})+"\n")

    return jsonify({"ts": ts, "command": cmd, "result": msg, "details": details})

# Payroll
@app.route("/api/payroll/preview", methods=["POST"])
def payroll_preview():
    body = request.get_json(force=True)
    total = float(body.get("total_pltr", 100.0))
    performance = body.get("performance", {})
    return jsonify({"preview": preview_allocation(total, performance)})

@app.route("/api/payroll/payout", methods=["POST"])
def payroll_payout():
    body = request.get_json(force=True)
    total = float(body.get("total_pltr", 100.0))
    performance = body.get("performance", {})
    initiator = body.get("initiator", "system")
    return jsonify(payout(total, performance, initiator))

if __name__ == "__main__":
    print(f"✅ Whalez-AI Gateway starting on http://127.0.0.1:{PORT}")
    app.run(host=BIND_HOST, port=PORT)

