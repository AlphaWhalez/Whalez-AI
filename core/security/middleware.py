"""FastAPI dependencies for enforcing token scopes."""

from __future__ import annotations

from typing import Callable, Iterable

from fastapi import Header, HTTPException

from .tokens import TokenService


def require_scopes(required: Iterable[str]) -> Callable:
    """Return a FastAPI dependency that validates bearer scopes."""

    required_scopes = set(required)

    async def _dep(authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing bearer token")

        token = authorization.split(" ", 1)[1]
        try:
            payload = TokenService().verify(token)
        except Exception as exc:  # noqa: BLE001 - bubble up as HTTP error
            raise HTTPException(status_code=401, detail="Invalid token") from exc

        scopes = set(payload.get("scopes", []))
        if not required_scopes.issubset(scopes):
            raise HTTPException(status_code=403, detail="Insufficient scope")
        return payload

    return _dep


__all__ = ["require_scopes"]
