"""Self-hosting automation utilities."""

from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from core.affirmation_core import AffirmationCore


class SelfHostingAgent:
    """Simulate deployment proofs by recording network reachability checks."""

    def __init__(self, data_dir: Path | str = Path("data")) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.proof_log = self.data_dir / "deployment_proofs.jsonl"
        self.manifest_path = self.data_dir / "domain_proof_manifest.json"
        self.core = AffirmationCore()

        if not self.manifest_path.exists():
            self.manifest_path.write_text(
                json.dumps({"dns": "pending", "ssl": "pending"}, indent=2),
                encoding="utf-8",
            )

    def record_deployment(self, provider: str, domain: str, note: str = "") -> Dict[str, str]:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "domain": domain,
            "note": note,
        }
        with open(self.proof_log, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")
        self.core.append(
            "Recorded deployment proof",
            {"provider": provider, "domain": domain, "note": note},
        )
        return payload

    def check_dns(self, hostname: str) -> Dict[str, str]:
        try:
            address = socket.gethostbyname(hostname)
            status = "resolved"
        except socket.gaierror:
            address = ""
            status = "unresolved"
        payload = {"hostname": hostname, "address": address, "status": status}
        manifest = self._read_manifest()
        manifest["dns"] = payload
        self._write_manifest(manifest)
        return payload

    def _read_manifest(self) -> Dict[str, object]:
        try:
            return json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _write_manifest(self, manifest: Dict[str, object]) -> None:
        self.manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["SelfHostingAgent"]
