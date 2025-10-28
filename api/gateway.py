#!/usr/bin/env python3
import os, json, random, time
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv

from src.agents.ledger_agent import LedgerAgent
from src.system import system_status_snapshot, verify_system_integrity
from src.payroll.engine import preview_allocation, payout

# env + settings
load_dotenv()
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5050"))
CORS_ALLOW = os.getenv("CORS_ALLOW", "*")
SSL_CERT = os.getenv("SSL_CERT", "")  # e.g. certs/cert.pem
SSL_KEY  = os.getenv("SSL_KEY", "")   # e.g. certs/key.pem

def _cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = CORS_ALLOW
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

app = Flask(__name__)
ledger_agent = LedgerAgent()

@app.after_request
def after(resp): return _cors_headers(resp)

@app.route("/")
def root():
    return "<h2>🐋 Whalez-AI Gateway</h2><p>/api/ping • /api/health • /api/agents/status • /api/payroll/preview</p>"

@app.route("/api/ping")
def ping(): return jsonify({"status": "Whalez-AI App Gateway online ✅", "port": PORT})

@app.route("/api/health")
def health():
    snap = system_status_snapshot(ledger_agent)
    return jsonify({"status": "online", "metrics": snap})

@app.route("/api/agents/status")
def agents_status():
    agents = [
        {"name": "InterfaceAgent", "status": random.choice(["active","idle","error"]),
         "last_heartbeat": datetime.utcnow().isoformat()+"Z",
         "task": random.choice(["Processing intent","Rendering","Idle","Syncing ledger"])},
        {"name": "LedgerAgent", "status": "active", "last_heartbeat": datetime.utcnow().isoformat()+"Z",
         "task": "Indexing blocks", "count": ledger_agent.count_blocks()}
    ]
    return jsonify({"agents": agents})

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json(force=True)
    cmd = (data.get("command") or "").strip().lower()
    ts = datetime.utcnow().isoformat()+"Z"
    if not cmd: return jsonify({"error": "Empty command"}), 400

    if cmd == "verify system integrity":
        details = verify_system_integrity(ledger_agent)
        msg = "✅ System integrity verified." if details.get("status")=="ok" else "⚠️ Attention required."
    elif cmd == "refresh ledger sync":
        details = ledger_agent.refresh()
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
    scheme = "https" if (SSL_CERT and SSL_KEY and os.path.exists(SSL_CERT) and os.path.exists(SSL_KEY)) else "http"
    print(f"✅ Whalez-AI Gateway starting on {scheme}://127.0.0.1:{PORT}")
    ssl_ctx = (SSL_CERT, SSL_KEY) if scheme == "https" else None
    app.run(host=BIND_HOST, port=PORT, ssl_context=ssl_ctx)
