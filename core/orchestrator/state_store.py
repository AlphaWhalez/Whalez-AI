# minimal state snapshot store (json on disk + in-memory cache)
from __future__ import annotations
import json, os, threading, time
from typing import Any, Dict

_DEFAULT_PATH = os.environ.get("STATE_SNAPSHOT_PATH", ".whalez/state.json")
_LOCK = threading.RLock()

class StateStore:
    def __init__(self, path: str = _DEFAULT_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self):
        with _LOCK:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
            else:
                self._cache = {}

    def save(self):
        with _LOCK:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, indent=2, sort_keys=True)
            os.replace(tmp, self.path)

    def set_service_state(self, name: str, status: str, meta: Dict[str, Any] | None = None):
        with _LOCK:
            self._cache.setdefault("services", {})
            self._cache["services"][name] = {
                "status": status,
                "meta": meta or {},
                "updated_at": int(time.time())
            }
            self.save()

    def get_service_state(self, name: str) -> Dict[str, Any] | None:
        return self._cache.get("services", {}).get(name)

    def snapshot(self) -> Dict[str, Any]:
        return dict(self._cache)
