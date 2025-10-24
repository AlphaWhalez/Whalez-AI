#!/usr/bin/env python3
# Whalez-US-Proxy: lightweight service registry + router + health monitor
# Pure stdlib: http.server + http.client + threading

import http.client
import http.server
import json
import os
import socketserver
import sys
import threading
import time
from typing import Dict, Tuple

# -------------------------
# Config (override via ENV)
# -------------------------
DEFAULT_ROUTES = {
    "interface": {"host": "127.0.0.1", "port": int(os.getenv("WHALEZ_INTERFACE_PORT", "8080"))},
    "vision": {"host": "127.0.0.1", "port": int(os.getenv("WHALEZ_VISION_PORT", "8088"))},
    "api": {"host": "127.0.0.1", "port": int(os.getenv("WHALEZ_API_PORT", "8090"))},
    "admin": {"host": "127.0.0.1", "port": int(os.getenv("WHALEZ_ADMIN_PORT", "9000"))},
    "sentinel": {"host": "127.0.0.1", "port": int(os.getenv("WHALEZ_SENTINEL_PORT", "9100"))},
}

PROXY_PORT = int(os.getenv("WHALEZ_PROXY_PORT", "8081"))
HEALTH_PERIOD = float(os.getenv("WHALEZ_HEALTH_PERIOD", "5"))  # seconds
HEALTH_TIMEOUT = float(os.getenv("WHALEZ_HEALTH_TIMEOUT", "1.5"))  # seconds
SHARED_SECRET = os.getenv("WHALEZ_SHARED_SECRET", "").strip()  # optional

# (path_prefix -> agent_name); everything after prefix is forwarded
ROUTE_PREFIXES = {
    "/interface/": "interface",
    "/vision/": "vision",
    "/api/": "api",
    "/admin/": "admin",
    "/sentinel/": "sentinel",
}


# -------------------------
# Service Registry
# -------------------------
class Registry:
    def __init__(self):
        self._lock = threading.RLock()
        self._targets: Dict[str, Dict] = {
            key: dict(value, healthy=False, last_ok=0.0) for key, value in DEFAULT_ROUTES.items()
        }

    def all(self):
        with self._lock:
            return json.loads(json.dumps(self._targets))

    def get(self, name: str):
        with self._lock:
            return self._targets.get(name)

    def set(self, name: str, host: str, port: int):
        with self._lock:
            current = self._targets.get(name, {})
            current.update({"host": host, "port": int(port)})
            # keep health fields if present
            current.setdefault("healthy", False)
            current.setdefault("last_ok", 0.0)
            self._targets[name] = current
            return json.loads(json.dumps(current))

    def mark_health(self, name: str, ok: bool):
        with self._lock:
            if name in self._targets:
                self._targets[name]["healthy"] = bool(ok)
                if ok:
                    self._targets[name]["last_ok"] = time.time()


REGISTRY = Registry()


# -------------------------
# Health Monitor
# -------------------------
def _probe(host: str, port: int) -> bool:
    try:
        conn = http.client.HTTPConnection(host, port, timeout=HEALTH_TIMEOUT)
        # try a generic path; many of our services respond to "/" or "/health"
        for path in ("/health", "/", "/status"):
            try:
                conn.request("GET", path)
                response = conn.getresponse()
                if 200 <= response.status < 500:  # treat non-5xx as up
                    return True
            except Exception:
                pass
        return False
    except Exception:
        return False


def health_thread():
    while True:
        for name, target in REGISTRY.all().items():
            ok = _probe(target["host"], int(target["port"]))
            REGISTRY.mark_health(name, ok)
        time.sleep(HEALTH_PERIOD)


# -------------------------
# HTTP Utilities
# -------------------------
def cors_headers(handler: http.server.BaseHTTPRequestHandler):
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Whalez-Secret")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")


def require_secret(handler: http.server.BaseHTTPRequestHandler) -> bool:
    if not SHARED_SECRET:
        return True
    given = handler.headers.get("X-Whalez-Secret", "")
    if given == SHARED_SECRET:
        return True
    handler.send_response(401)
    cors_headers(handler)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(b'{"error":"unauthorized"}')
    return False


def parse_json(handler: http.server.BaseHTTPRequestHandler):
    length = int(handler.headers.get("Content-Length", "0") or 0)
    if length <= 0:
        return {}
    data = handler.rfile.read(length)
    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        return {}


def forward(
    handler: http.server.BaseHTTPRequestHandler,
    target: Dict,
    method: str,
    path: str,
    body: bytes,
):
    conn = http.client.HTTPConnection(target["host"], int(target["port"]), timeout=15)
    # Propagate headers except hop-by-hop
    headers = {
        key: value
        for key, value in handler.headers.items()
        if key.lower()
        not in {
            "host",
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        }
    }
    try:
        conn.request(method, path, body=body if body else None, headers=headers)
        response = conn.getresponse()
        handler.send_response(response.status)
        # copy response headers
        for key, value in response.getheaders():
            if key.lower() != "transfer-encoding":  # avoid chunking confusion
                handler.send_header(key, value)
        cors_headers(handler)
        handler.end_headers()
        chunk = response.read()
        if chunk:
            handler.wfile.write(chunk)
    except Exception as error:
        payload = json.dumps({"error": "upstream_unreachable", "detail": str(error)}).encode("utf-8")
        handler.send_response(502)
        cors_headers(handler)
        handler.send_header("Content-Type", "application/json")
        handler.send_header("Content-Length", str(len(payload)))
        handler.end_headers()
        handler.wfile.write(payload)
    finally:
        try:
            conn.close()
        except Exception:
            pass


def route_target(path: str) -> Tuple[str, Dict, str]:
    for prefix, name in ROUTE_PREFIXES.items():
        if path.startswith(prefix):
            target = REGISTRY.get(name)
            # strip the prefix when forwarding
            new_path = "/" + path[len(prefix) :].lstrip("/")
            return name, target, new_path
    return "", None, path


# -------------------------
# HTTP Handler
# -------------------------
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    server_version = "WhalezUSProxy/1.0"

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def _handle_api(self, method: str):
        # /health -> global health snapshot
        if self.path == "/health":
            snapshot = REGISTRY.all()
            body = json.dumps({"proxy": {"port": PROXY_PORT}, "services": snapshot, "time": time.time()}).encode(
                "utf-8"
            )
            self.send_response(200)
            cors_headers(self)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # /routes -> list route prefixes and service map
        if self.path == "/routes":
            body = json.dumps({"prefixes": ROUTE_PREFIXES, "targets": REGISTRY.all()}).encode("utf-8")
            self.send_response(200)
            cors_headers(self)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # /register -> POST {name, host, port}
        if self.path == "/register":
            if method != "POST":
                self.send_response(405)
                cors_headers(self)
                self.end_headers()
                return
            if not require_secret(self):
                return
            data = parse_json(self)
            name = str(data.get("name", "")).strip()
            host = str(data.get("host", "")).strip() or "127.0.0.1"
            port = int(data.get("port", 0))
            if not name or not port:
                self.send_response(400)
                cors_headers(self)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"error":"name_and_port_required"}')
                return
            result = REGISTRY.set(name, host, port)
            self.send_response(200)
            cors_headers(self)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
            return

        # Not a management path; try to route by prefix
        name, target, new_path = route_target(self.path)
        if not target:
            self.send_response(404)
            cors_headers(self)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "no_route", "path": self.path}).encode("utf-8"))
            return

        # Read body for mutating verbs
        body = None
        if method in ("POST", "PUT", "PATCH"):
            length = int(self.headers.get("Content-Length", "0") or 0)
            body = self.rfile.read(length) if length > 0 else None
        forward(self, target, method, new_path, body)

    def do_GET(self):  # noqa: N802 - http.server naming
        self._handle_api("GET")

    def do_POST(self):  # noqa: N802 - http.server naming
        self._handle_api("POST")

    def do_PUT(self):  # noqa: N802 - http.server naming
        self._handle_api("PUT")

    def do_PATCH(self):  # noqa: N802 - http.server naming
        self._handle_api("PATCH")

    def do_DELETE(self):  # noqa: N802 - http.server naming
        self._handle_api("DELETE")

    def log_message(self, fmt, *args):
        sys.stdout.write(f"[Proxy] {self.address_string()} {self.command} {self.path} -> {fmt % args}\n")


# -------------------------
# Main
# -------------------------
def main():
    # kick off health thread
    thread = threading.Thread(target=health_thread, daemon=True)
    thread.start()

    with socketserver.ThreadingTCPServer(("", PROXY_PORT), ProxyHandler) as httpd:
        httpd.allow_reuse_address = True
        print(f"🌐 Whalez-US-Proxy up on :{PROXY_PORT}")
        try:
            httpd.serve_forever(poll_interval=0.5)
        except KeyboardInterrupt:
            print("🛑 Proxy shutting down...")


if __name__ == "__main__":
    main()
