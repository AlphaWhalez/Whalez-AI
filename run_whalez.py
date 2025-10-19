"""Launcher for the Whalez-AI sovereign stack."""

from __future__ import annotations

from core.affirmation_core import AffirmationCore
from core.self_domain import record_subdomain
from src.agents import InterfaceAgent, SecurityAgent, SelfHostingAgent


def main() -> None:
    core = AffirmationCore()
    security = SecurityAgent()
    interface = InterfaceAgent(security_agent=security)
    self_hosting = SelfHostingAgent()

    subdomain = record_subdomain(core)
    core.append("Starting interface agent", {"port": interface.port})
    self_hosting.record_deployment("local-dev", subdomain, note="launcher start")

    print("Whalez-AI Sovereign Stack ready")
    print(f"Interface: http://{interface.host}:{interface.port}")
    print(f"Deterministic subdomain: {subdomain}")
    interface.start()


if __name__ == "__main__":
    main()
