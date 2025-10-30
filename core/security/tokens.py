"""Scoped service tokens based on JWT HS256."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Sequence

try:  # pragma: no cover - optional dependency for light test envs
    import jwt
except Exception:  # pragma: no cover
    class _MissingJWTModule:
        def __getattr__(self, item):
            raise RuntimeError("PyJWT is required for token operations")

    jwt = _MissingJWTModule()  # type: ignore[assignment]


class TokenService:
    """Utility for minting and verifying JWT-based service tokens."""

    def __init__(self, secret: str | None = None) -> None:
        self.secret = secret or os.getenv("TOKEN_SECRET", "dev-token-secret")

    def mint(self, subject: str, scopes: Sequence[str], ttl_s: int = 3600) -> str:
        now = int(time.time())
        payload = {
            "sub": subject,
            "scopes": list(scopes),
            "iat": now,
            "exp": now + ttl_s,
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def verify(self, token: str) -> Dict[str, Any]:
        return jwt.decode(token, self.secret, algorithms=["HS256"])


__all__ = ["TokenService"]
