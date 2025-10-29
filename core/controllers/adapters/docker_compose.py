"""Placeholder adapter that would delegate orchestration to docker-compose.

The blueprint keeps the module minimal for now.  It provides structure so that
future iterations can plug into ``docker compose`` when the stack graduates from
local process supervision.
"""

from __future__ import annotations

from typing import Dict


class DockerComposeAdapter:
    name = "docker_compose"

    def __init__(self, project_file: str = "docker-compose.yml") -> None:
        self.project_file = project_file

    def start(self, service_def, variant: str = "primary") -> Dict[str, object]:  # pragma: no cover - stub
        raise NotImplementedError("docker-compose adapter is not yet implemented")

    def stop(self, service_name: str, variant: str) -> Dict[str, object]:  # pragma: no cover - stub
        raise NotImplementedError("docker-compose adapter is not yet implemented")

    def promote(self, service_name: str, *, source_variant: str, target_variant: str) -> Dict[str, object]:  # pragma: no cover - stub
        raise NotImplementedError("docker-compose adapter is not yet implemented")

    def describe(self) -> Dict[str, Dict[str, object]]:  # pragma: no cover - stub
        raise NotImplementedError("docker-compose adapter is not yet implemented")


__all__ = ["DockerComposeAdapter"]
