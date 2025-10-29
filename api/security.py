"""Security-focused FastAPI routes (tokens + secrets)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from core.security.middleware import require_scopes
from core.security.tokens import TokenService
from core.security.vault import Vault

router = APIRouter(prefix="/security", tags=["security"])
_token_service = TokenService()
_vault = Vault()


class TokenRequest(BaseModel):
    subject: str
    scopes: list[str] = Field(default_factory=lambda: ["read:secrets"])
    ttl_s: int = 3600


class SecretRequest(BaseModel):
    key: str
    value: str


@router.post("/auth/token")
def mint_token(request: TokenRequest):
    """Mint a scoped token for a given subject."""

    return {
        "token": _token_service.mint(
            request.subject, request.scopes, ttl_s=request.ttl_s
        )
    }


@router.get("/auth/verify")
def verify_token(payload=Depends(require_scopes([]))):
    """Verify bearer token validity and return the payload."""

    return {"ok": True, "payload": payload}


@router.post("/secrets/set")
def set_secret(
    request: SecretRequest,
    _payload=Depends(require_scopes(["write:secrets"])),
):
    """Store an encrypted secret in the vault."""

    _vault.set(request.key, request.value)
    return {"ok": True}


@router.get("/secrets/get")
def get_secret(
    key: str = Query(...),
    _payload=Depends(require_scopes(["read:secrets"])),
):
    """Retrieve an encrypted secret from the vault (if present)."""

    return {"value": _vault.get(key)}


__all__ = ["router"]
