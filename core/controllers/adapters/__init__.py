"""Execution adapters for the governance orchestrator."""

from .local_process import LocalProcessAdapter  # noqa: F401
from .docker_compose import DockerComposeAdapter  # noqa: F401
