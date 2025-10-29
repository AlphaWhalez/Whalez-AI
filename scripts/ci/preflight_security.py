"""CI smoke-test for the security stack (vault + tokens)."""

from __future__ import annotations

from core.security.tokens import TokenService
from core.security.vault import Vault


def main() -> None:
    vault = Vault(".secrets-ci")
    vault.set("smoke", "ok")
    assert vault.get("smoke") == "ok", "vault round-trip failed"

    service = TokenService("ci-secret")
    token = service.mint("ci", ["read:secrets", "write:secrets"])
    payload = service.verify(token)
    assert "read:secrets" in payload.get("scopes", []), "missing scope"
    print("SECURITY_PREFLIGHT_OK")


if __name__ == "__main__":
    main()
