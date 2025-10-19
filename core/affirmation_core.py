"""Affirmation core module for Whalez-AI.

Provides append-only affirmation logging that ties entries to the
Whalez identity configuration. The module intentionally avoids any
external dependencies so it can run in constrained environments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from threading import Lock
from typing import Iterable, Dict, Any, Optional
from datetime import datetime, timezone


class AffirmationError(RuntimeError):
    """Base exception for affirmation related errors."""


class IdentityLoadError(AffirmationError):
    """Raised when the Whalez identity configuration cannot be loaded."""


@dataclass
class WhalezIdentity:
    """Dataclass representation of the Whalez identity file."""

    identity_name: str
    founder_hash: str
    public_key_fingerprint: str
    domain_seed: str
    affirmation_log: str = "data/affirmations.jsonl"
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: os.PathLike[str] | str) -> "WhalezIdentity":
        try:
            with open(path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except OSError as exc:  # pragma: no cover - defensive logging only
            raise IdentityLoadError(f"Unable to read identity file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise IdentityLoadError(
                f"Identity file {path} contains invalid JSON"
            ) from exc

        required_keys = {"identity_name", "founder_hash", "public_key_fingerprint", "domain_seed"}
        missing = required_keys - payload.keys()
        if missing:
            raise IdentityLoadError(
                f"Identity file missing required fields: {', '.join(sorted(missing))}"
            )

        return cls(
            identity_name=payload["identity_name"],
            founder_hash=payload["founder_hash"],
            public_key_fingerprint=payload["public_key_fingerprint"],
            domain_seed=payload["domain_seed"],
            affirmation_log=payload.get("affirmation_log", "data/affirmations.jsonl"),
            raw=payload,
        )


class AffirmationCore:
    """Append-only affirmation store bound to a Whalez identity."""

    def __init__(self, identity_path: os.PathLike[str] | str = "core/whalez_identity.json"):
        self._identity_path = Path(identity_path)
        self.identity = WhalezIdentity.from_file(self._identity_path)
        self._log_path = Path(self.identity.affirmation_log)
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

        # Ensure the log file exists to simplify downstream consumers.
        if not self._log_path.exists():
            self._log_path.touch()

    @property
    def log_path(self) -> Path:
        return self._log_path

    def append(self, message: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Append a new affirmation entry to the JSONL log.

        Args:
            message: Human readable text affirming an event or state change.
            metadata: Optional mapping with additional contextual information.
        Returns:
            The record that was persisted to disk.
        """

        metadata = metadata or {}
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "identity": self.identity.identity_name,
            "founder_hash": self.identity.founder_hash,
            "message": message,
            "metadata": metadata,
        }

        serialized = json.dumps(entry, sort_keys=True)
        with self._lock:
            with open(self._log_path, "a", encoding="utf-8") as handle:
                handle.write(serialized + "\n")
        return entry

    def iter_entries(self) -> Iterable[Dict[str, Any]]:
        """Iterate through log entries in the order they were written."""

        with self._lock:
            with open(self._log_path, "r", encoding="utf-8") as handle:
                for line in handle:
                    if not line.strip():
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue  # gracefully skip malformed lines

    def latest(self) -> Optional[Dict[str, Any]]:
        """Return the most recent affirmation entry or ``None``."""

        latest_entry: Optional[Dict[str, Any]] = None
        for entry in self.iter_entries():
            latest_entry = entry
        return latest_entry


__all__ = ["AffirmationCore", "AffirmationError", "IdentityLoadError", "WhalezIdentity"]
