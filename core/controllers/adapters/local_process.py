"""Adapter that supervises services as local OS processes.

The adapter defaults to ``dry_run`` mode so that development environments can
exercise orchestration logic without spawning long-running processes.  Pass
``dry_run=False`` (see :mod:`scripts/linux/start_orchestrator.sh`) to enable
actual process management.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional


class LocalProcessAdapter:
    name = "local_process"

    def __init__(self, *, state_dir: Path | str = Path("logs/governance"), dry_run: bool = True) -> None:
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "local_process_state.json"
        self.instances: Dict[str, Dict[str, Dict[str, object]]] = self._load_state()
        self._process_handles: Dict[str, subprocess.Popen] = {}
        self.dry_run = dry_run

    # ------------------------------------------------------------------
    def _load_state(self) -> Dict[str, Dict[str, Dict[str, object]]]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {}
        return {}

    def _persist(self) -> None:
        self.state_file.write_text(
            json.dumps(self.instances, indent=2, sort_keys=True), encoding="utf-8"
        )

    def _handle_key(self, service_name: str, variant: str) -> str:
        return f"{service_name}:{variant}"

    # ------------------------------------------------------------------
    def start(self, service_def, variant: str = "primary") -> Dict[str, object]:
        entries = self.instances.setdefault(service_def.name, {})
        info = {
            "variant": variant,
            "command": service_def.command,
            "ports": service_def.ports,
            "env": service_def.env,
            "host": "127.0.0.1",
            "port": service_def.ports[0] if service_def.ports else None,
            "timestamp": time.time(),
            "dry_run": self.dry_run,
        }
        if not self.dry_run:
            env = os.environ.copy()
            env.update(service_def.env or {})
            env["WHALEZ_VARIANT"] = variant
            proc = subprocess.Popen(service_def.command, shell=True, env=env)
            info["pid"] = proc.pid
            self._process_handles[self._handle_key(service_def.name, variant)] = proc
        else:
            info["pid"] = None
        entries[variant] = info
        self._persist()
        return info

    def stop(self, service_name: str, variant: str) -> Optional[Dict[str, object]]:
        entries = self.instances.get(service_name)
        if not entries:
            return None
        info = entries.pop(variant, None)
        if info is None:
            return None
        handle_key = self._handle_key(service_name, variant)
        handle = self._process_handles.pop(handle_key, None)
        if handle and handle.poll() is None:
            handle.terminate()
        if not entries:
            self.instances.pop(service_name, None)
        self._persist()
        return info

    def promote(self, service_name: str, *, source_variant: str, target_variant: str) -> Dict[str, object]:
        entries = self.instances.setdefault(service_name, {})
        info = entries.pop(source_variant)
        info["variant"] = target_variant
        entries[target_variant] = info
        source_key = self._handle_key(service_name, source_variant)
        target_key = self._handle_key(service_name, target_variant)
        handle = self._process_handles.pop(source_key, None)
        if handle is not None:
            self._process_handles[target_key] = handle
        self._persist()
        return info

    def describe(self) -> Dict[str, Dict[str, Dict[str, object]]]:
        return json.loads(json.dumps(self.instances))


__all__ = ["LocalProcessAdapter"]
