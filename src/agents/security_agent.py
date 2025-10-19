"""Security instrumentation utilities for Whalez-AI."""

from __future__ import annotations

import json
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Dict, Optional


@dataclass
class SecurityIncident:
    timestamp: float
    incident_type: str
    client_ip: str
    details: Dict[str, str]

    def to_json(self) -> str:
        payload = {
            "timestamp": self.timestamp,
            "incident_type": self.incident_type,
            "client_ip": self.client_ip,
            "details": self.details,
        }
        return json.dumps(payload, sort_keys=True)


class SecurityAgent:
    """Record HTTP level security signals.

    The agent focuses on defensive monitoring: rate limiting and simple
    brute-force detection. Incidents are appended to
    ``data/security_incidents.jsonl`` and blocked IPs are stored in
    ``data/blocked_ips.txt`` to be reused by upstream infrastructure.
    """

    def __init__(
        self,
        data_dir: Path | str = Path("data"),
        enabled: bool = True,
        window_seconds: int = 60,
        max_requests_per_window: int = 120,
        max_auth_failures: int = 5,
    ) -> None:
        self.enabled = enabled
        self.data_dir = Path(data_dir)
        self.window_seconds = window_seconds
        self.max_requests_per_window = max_requests_per_window
        self.max_auth_failures = max_auth_failures

        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.incident_path = self.data_dir / "security_incidents.jsonl"
        self.blocklist_path = self.data_dir / "blocked_ips.txt"
        self.request_log: Dict[str, Deque[float]] = defaultdict(deque)
        self.auth_failures: Dict[str, int] = defaultdict(int)
        self.blocked_ips: set[str] = set()

        if self.blocklist_path.exists():
            with open(self.blocklist_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if line:
                        self.blocked_ips.add(line)

    def _append_incident(self, incident: SecurityIncident) -> None:
        if not self.enabled:
            return
        with open(self.incident_path, "a", encoding="utf-8") as handle:
            handle.write(incident.to_json() + "\n")

    def _persist_blocklist(self) -> None:
        with open(self.blocklist_path, "w", encoding="utf-8") as handle:
            for ip in sorted(self.blocked_ips):
                handle.write(f"{ip}\n")

    def record_request(self, client_ip: str, path: str) -> None:
        if not self.enabled:
            return
        now = time.time()
        queue = self.request_log[client_ip]
        queue.append(now)
        while queue and now - queue[0] > self.window_seconds:
            queue.popleft()
        if len(queue) > self.max_requests_per_window and client_ip not in self.blocked_ips:
            incident = SecurityIncident(
                timestamp=now,
                incident_type="rate_limit",
                client_ip=client_ip,
                details={"path": path, "count": str(len(queue))},
            )
            self._append_incident(incident)
            self.block_ip(client_ip, reason="Rate limit exceeded")

    def record_auth_failure(self, client_ip: str, username: Optional[str] = None) -> None:
        if not self.enabled:
            return
        self.auth_failures[client_ip] += 1
        failures = self.auth_failures[client_ip]
        if failures >= self.max_auth_failures:
            incident = SecurityIncident(
                timestamp=time.time(),
                incident_type="auth_bruteforce",
                client_ip=client_ip,
                details={"username": username or "unknown", "failures": str(failures)},
            )
            self._append_incident(incident)
            self.block_ip(client_ip, reason="Too many authentication failures")

    def block_ip(self, client_ip: str, reason: str) -> None:
        if client_ip in self.blocked_ips:
            return
        self.blocked_ips.add(client_ip)
        incident = SecurityIncident(
            timestamp=time.time(),
            incident_type="ip_block",
            client_ip=client_ip,
            details={"reason": reason},
        )
        self._append_incident(incident)
        self._persist_blocklist()

    def is_blocked(self, client_ip: str) -> bool:
        return client_ip in self.blocked_ips

    def snapshot(self) -> Dict[str, object]:
        return {
            "enabled": self.enabled,
            "blocked_ips": sorted(self.blocked_ips),
            "window_seconds": self.window_seconds,
            "max_requests_per_window": self.max_requests_per_window,
            "max_auth_failures": self.max_auth_failures,
        }


__all__ = ["SecurityAgent"]
