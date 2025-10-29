"""Registry for desired service state declared in ``config/services.yaml``.

The registry is intentionally strict: it validates schema details and normalises
values so that downstream components can rely on consistent types.  The module
is lightweight on purpose – it only deals with configuration, not with runtime
status.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional
import yaml

__all__ = [
    "ServiceRegistry",
    "ServiceDefinition",
    "ServiceHealthConfig",
    "ServiceRolloutConfig",
]


def _parse_interval(value: str) -> float:
    """Translate a compact interval notation (``5s``, ``2m``) into seconds."""
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str):  # pragma: no cover - defensive
        raise ValueError(f"Unsupported interval type: {type(value)!r}")
    value = value.strip().lower()
    if value.endswith("ms"):
        return float(value[:-2]) / 1000.0
    multiplier = 1.0
    if value.endswith("s"):
        multiplier = 1.0
        value = value[:-1]
    elif value.endswith("m"):
        multiplier = 60.0
        value = value[:-1]
    elif value.endswith("h"):
        multiplier = 3600.0
        value = value[:-1]
    return float(value) * multiplier


def _parse_thresholds(definition: Dict[str, str]) -> Dict[str, str]:
    parsed: Dict[str, str] = {}
    for key, raw in definition.items():
        parsed[key] = str(raw).strip()
    return parsed


@dataclass
class ServiceHealthConfig:
    probe_type: str
    path: str
    interval_seconds: float = 30.0
    timeout_seconds: float = 5.0
    slo: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, name: str, payload: Dict[str, object]) -> "ServiceHealthConfig":
        probe = payload.get("probe") or {}
        slo = payload.get("slo") or {}
        probe_type = str(probe.get("type", "http")).lower()
        path = str(probe.get("path", "/"))
        interval_seconds = _parse_interval(probe.get("interval", "30s"))
        timeout_seconds = _parse_interval(probe.get("timeout", "5s"))
        return cls(
            probe_type=probe_type,
            path=path,
            interval_seconds=interval_seconds,
            timeout_seconds=timeout_seconds,
            slo=_parse_thresholds(slo),
        )


@dataclass
class ServiceRolloutConfig:
    strategy: str = "canary"
    canary_percent: int = 0
    pause_seconds: float = 0.0

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "ServiceRolloutConfig":
        strategy = str(payload.get("strategy", "canary")).lower()
        canary_percent = int(payload.get("canary_percent", 0))
        pause_seconds = _parse_interval(payload.get("pause_seconds", 0))
        return cls(strategy=strategy, canary_percent=canary_percent, pause_seconds=pause_seconds)


@dataclass
class ServiceDefinition:
    name: str
    service_type: str
    command: str
    env: Dict[str, str] = field(default_factory=dict)
    ports: List[int] = field(default_factory=list)
    health: Optional[ServiceHealthConfig] = None
    rollout: Optional[ServiceRolloutConfig] = None

    @classmethod
    def from_dict(cls, name: str, payload: Dict[str, object]) -> "ServiceDefinition":
        service_type = str(payload.get("type", "process")).lower()
        command = payload.get("command")
        if not command:
            raise ValueError(f"service '{name}' is missing a command")
        env = {str(k): str(v) for k, v in (payload.get("env") or {}).items()}
        ports = [int(p) for p in payload.get("ports", [])]
        health_cfg = payload.get("health")
        rollout_cfg = payload.get("rollout")
        health = ServiceHealthConfig.from_dict(name, health_cfg) if health_cfg else None
        rollout = ServiceRolloutConfig.from_dict(rollout_cfg) if rollout_cfg else None
        return cls(
            name=name,
            service_type=service_type,
            command=str(command),
            env=env,
            ports=ports,
            health=health,
            rollout=rollout,
        )


class ServiceRegistry:
    """Load and validate desired service state."""

    def __init__(self, config_path: Path | str = Path("config/services.yaml")) -> None:
        self.config_path = Path(config_path)
        self._services: Dict[str, ServiceDefinition] = {}
        self.version: Optional[int] = None

    def load(self) -> None:
        if not self.config_path.exists():
            raise FileNotFoundError(self.config_path)
        payload = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        self.version = int(payload.get("version", 1))
        services_block = payload.get("services") or {}
        services: Dict[str, ServiceDefinition] = {}
        for name, definition in services_block.items():
            services[name] = ServiceDefinition.from_dict(name, definition)
        self._services = services

    @property
    def services(self) -> Dict[str, ServiceDefinition]:
        if not self._services:
            self.load()
        return self._services

    def __iter__(self) -> Iterable[ServiceDefinition]:
        return iter(self.services.values())

    def get(self, name: str) -> Optional[ServiceDefinition]:
        return self.services.get(name)

    def as_dict(self) -> Dict[str, Dict[str, object]]:
        result: Dict[str, Dict[str, object]] = {}
        for service in self:
            result[service.name] = {
                "type": service.service_type,
                "command": service.command,
                "env": service.env,
                "ports": service.ports,
                "health": service.health.__dict__ if service.health else None,
                "rollout": service.rollout.__dict__ if service.rollout else None,
            }
        return result


def load_desired_state(config_path: Path | str = Path("config/services.yaml")) -> Dict[str, ServiceDefinition]:
    registry = ServiceRegistry(config_path)
    registry.load()
    return registry.services
