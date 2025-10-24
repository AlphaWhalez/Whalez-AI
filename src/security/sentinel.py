#!/usr/bin/env python3
"""
Whalez-AI Sentinel Security Watchdog
Responsible for runtime integrity verification, process monitoring,
and alerting of anomalies within Whalez-AI services.
"""

import os, time, json, hashlib, threading, psutil, subprocess, http.client

SENTINEL_PORT = int(os.getenv("WHALEZ_SENTINEL_PORT", "9100"))
HEALTH_INTERVAL = int(os.getenv("WHALEZ_HEALTH_INTERVAL", "10"))
WATCH_PROCESSES = ["Whalez-US-Proxy", "AdminConsole"]

# --------------------------------
# Health + Integrity Checks
# --------------------------------
def get_pm2_status():
    try:
        result = subprocess.run(["pm2", "jlist"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return json.loads(result.stdout or "[]")
    except Exception as e:
        return [{"error": str(e)}]
    return []

def check_integrity():
    # hash sentinel file itself as a simple integrity proof
    path = os.path.realpath(__file__)
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest()

def collect_stats():
    return {
        "cpu": psutil.cpu_percent(interval=0.2),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }

# --------------------------------
# Background health monitor
# --------------------------------
def monitor_loop():
    while True:
        pm2 = get_pm2_status()
        status = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "integrity": check_integrity(),
            "system": collect_stats(),
            "pm2": pm2,
        }
        print(f"[Sentinel] heartbeat: {json.dumps(status)[:200]}...")
        time.sleep(HEALTH_INTERVAL)

# --------------------------------
# HTTP health endpoint
# --------------------------------
from http.server import BaseHTTPRequestHandler, HTTPServer

class SentinelHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            payload = json.dumps({
                "status": "ok",
                "integrity": check_integrity(),
                "system": collect_stats(),
                "time": time.time()
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    httpd = HTTPServer(("", SENTINEL_PORT), SentinelHandler)
    print(f"🛡  Sentinel active on port {SENTINEL_PORT}")
    threading.Thread(target=monitor_loop, daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("🛑 Sentinel shutting down...")

if __name__ == "__main__":
    run_server()
