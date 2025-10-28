# Maps HTTPS serving → Flask app instance
import os
from flask import Flask, redirect

def attach_http_redirect(app: Flask, target_https_port: int):
    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def _redir(path):
        host = os.getenv("WHALEZ_DOMAIN_HOST", "127.0.0.1")
        return redirect(f"https://{host}:{target_https_port}/{path}", code=302)
