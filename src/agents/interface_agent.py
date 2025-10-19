"""HTTP interface agent serving the Whalez sovereign UI."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from flask import Flask, jsonify, request, send_from_directory

from core.affirmation_core import AffirmationCore
from core.self_domain import deterministic_subdomain
from .security_agent import SecurityAgent


class InterfaceAgent:
    """Expose a lightweight HTTP interface for the Whalez stack."""

    def __init__(
        self,
        web_root: Path | str = Path("web"),
        host: str = "0.0.0.0",
        port: int = 8080,
        security_agent: Optional[SecurityAgent] = None,
    ) -> None:
        self.web_root = Path(web_root).resolve()
        self.host = host
        self.port = port
        self.security_agent = security_agent or SecurityAgent(enabled=False)
        self.core = AffirmationCore()
        self._app = self._create_app()

    def _create_app(self) -> Flask:
        app = Flask(__name__, static_folder=str(self.web_root), static_url_path="")

        @app.before_request
        def _before_request() -> None:
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            self.security_agent.record_request(client_ip=client_ip, path=request.path)
            if self.security_agent.is_blocked(client_ip):
                return (jsonify({"error": "blocked"}), 429)
            return None

        @app.route("/")
        def index() -> tuple[str, int] | str:
            index_path = self.web_root / "index.html"
            if index_path.exists():
                return app.send_static_file("index.html")
            return "Interface not provisioned", 501

        @app.route("/manifest.json")
        def manifest() -> tuple[str, int] | str:
            manifest_path = self.web_root / "manifest.json"
            if manifest_path.exists():
                return app.send_static_file("manifest.json")
            return (jsonify({"error": "manifest missing"}), 404)

        @app.route("/health")
        def health() -> tuple[str, int]:
            status = {
                "status": "ok",
                "identity": self.core.identity.identity_name,
                "subdomain": deterministic_subdomain(self.core.identity),
                "latest_affirmation": self.core.latest(),
                "security": self.security_agent.snapshot(),
            }
            return jsonify(status), 200

        @app.route("/api/affirm", methods=["POST"])
        def affirm() -> tuple[str, int]:
            payload = request.get_json(force=True, silent=True) or {}
            message = payload.get("message", "")
            if not message:
                return jsonify({"error": "message required"}), 400
            entry = self.core.append(message, metadata={"source": "interface"})
            return jsonify(entry), 201

        return app

    @property
    def app(self) -> Flask:
        return self._app

    def start(self, **kwargs) -> None:
        """Start the HTTP server."""

        self._app.run(host=self.host, port=self.port, **kwargs)


__all__ = ["InterfaceAgent"]
