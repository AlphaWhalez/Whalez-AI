#!/usr/bin/env python3
"""
Whalez-AI Admin Console Server
Serves as a local admin and telemetry dashboard endpoint.
"""

import os, json, http.server, socketserver, time, subprocess

PORT = int(os.getenv("WHALEZ_ADMIN_PORT", "9000"))

# -------------------------
# Telemetry Fetcher
# -------------------------
def get_pm2_status():
    try:
        result = subprocess.run(
            ["pm2", "jlist"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout or "[]")
    except Exception as e:
        return [{"error": str(e)}]
    return []

def get_system_stats():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        return {"cpu": cpu, "mem": mem}
    except Exception:
        return {"cpu": "n/a", "mem": "n/a"}

# -------------------------
# HTTP Handler
# -------------------------
class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[AdminConsole] {self.address_string()} - {format % args}")

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/dashboard"):
            data = {
                "status": "running",
                "time": time.time(),
                "system": get_system_stats(),
                "pm2": get_pm2_status(),
            }
            payload = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

# -------------------------
# Main Server
# -------------------------
def main():
    print(f"🖥  Whalez-AI Admin Console running on port {PORT}")
    with socketserver.ThreadingTCPServer(("", PORT), AdminHandler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("🛑 Admin Console shutting down...")

if __name__ == "__main__":
    main()
