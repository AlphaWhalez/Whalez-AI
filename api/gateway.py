#!/usr/bin/env python3
import os, json, random, time, traceback, logging
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv

from src.agents.ledger_agent import LedgerAgent
from src.system import system_status_snapshot, verify_system_integrity
from src.payroll.engine import preview_allocation, payout

# env
load_dotenv()
BIND_HOST = os.getenv("BIND_HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", os.getenv("SERVICE_PORT", "5050")))
CORS_ALLOW = os.getenv("CORS_ALLOW", "*")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

# logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.FileHandler("logs/gateway.log", encoding="utf-8"),
        logging.StreamHandler()
    ],
)
log = logging.getLogger("gateway")

def _cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = CORS_ALLOW
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp

app = Flask(__name__)
app.secret_key = SECRET_KEY
ledger_agent = LedgerAgent()

@app.after_request
def after(resp):
    return _cors_headers(resp)

# ---------- health / meta ----------
@app.route("/")
def root():
    return "<h2>🐋 Whalez-AI Gateway</h2><p>See /api/ping, /api/health, /api/agents/status</p>"

@app.route("/api/version")
def version():
    return jsonify({"service":"whalez-ai-gateway","version":"v2.0-stage4","port":PORT})

@app.route("/api/ping")
def ping():
    return jsonify({"status": "Whalez-AI online ✅", "port": PORT, "version":"v2.0-stage4"})

@app.route("/api/health")
def health():
    snap = system_status_snapshot(ledger_agent)
    return jsonify({"status": "online", "metrics": snap})

# ---------- agents ----------
@app.route("/api/agents/status")
def agents_status():
    from datetime import timezone
    agents = [
        {"name": "InterfaceAgent", "status": "active",
         "last_heartbeat": datetime.now(timezone.utc).isoformat(),
         "task": "Orchestrating intents"},
        {"name": "LedgerAgent", "status": "active",
         "last_heartbeat": datetime.utcnow().isoformat()+"Z",
         "task": "Indexing", "count": ledger_agent.count_blocks()}
    ]
    return jsonify({"agents": agents})

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json(force=True)
    cmd = (data.get("command") or "").strip().lower()
    ts = datetime.utcnow().isoformat()+"Z"
    if not cmd:
        return jsonify({"error": "Empty command"}), 400
    if cmd == "verify system integrity":
        details = verify_system_integrity(ledger_agent); msg = "✅ Integrity ok" if details.get("status")=="ok" else "⚠️ Check"
    elif cmd == "refresh ledger sync":
        details = ledger_agent.refresh(); msg = f"🔄 Ledger synchronized — {details.get('count',0)} block(s)."
    else:
        details = {}; msg = f"⚙️ Command '{cmd}' executed (stub)."
    os.makedirs("data", exist_ok=True)
    with open("data/command_log.jsonl","a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": ts, "command": cmd, "result": msg, "details": details})+"\n")
    return jsonify({"ts": ts, "result": msg, "details": details})

# ---------- payroll ----------
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

# ---------- telemetry ----------
TELEMETRY = "data/telemetry.jsonl"
os.makedirs("data", exist_ok=True)

@app.route("/api/telemetry/heartbeat", methods=["POST"])
def telemetry_heartbeat():
    payload = request.get_json(force=True)
    payload["ts"] = int(time.time())
    with open(TELEMETRY, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload) + "\n")
    return jsonify({"ok": True})

@app.errorhandler(Exception)
def on_error(e):
    tb = traceback.format_exc()
    log.error("Unhandled error: %s", tb)
    with open(TELEMETRY, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": int(time.time()),
            "type": "error",
            "message": str(e),
            "trace": tb
        })+"\n")
    return jsonify({"error":"internal_error"}), 500

if __name__ == "__main__":
    print(f"✅ Whalez-AI Gateway starting on http://127.0.0.1:{PORT}")
    # For production runners (Gunicorn/Waitress) we don't call app.run
    app.run(host=BIND_HOST, port=PORT)
