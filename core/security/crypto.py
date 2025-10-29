"""Crypto helpers for the encrypted secrets vault."""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass

from cryptography.fernet import Fernet


@dataclass(slots=True)
class KdfParams:
    """Parameters used to derive a deterministic Fernet key."""

    salt: str = "whalez-ai-default-salt"
    rounds: int = 100_000


def _derive_key(master: str, salt: str, rounds: int) -> bytes:
    """Derive a URL-safe 32 byte key from the provided inputs."""

    dk = hashlib.pbkdf2_hmac(
        "sha256",
        master.encode(),
        salt.encode(),
        rounds,
        dklen=32,
    )
    return base64.urlsafe_b64encode(dk)


def fernet_from_env(master: str | None = None, params: KdfParams | None = None) -> Fernet:
    """Create a Fernet instance using environment configuration."""

    params = params or KdfParams()
    master = master or os.getenv("VAULT_MASTER_KEY", "dev-master-key")
    return Fernet(_derive_key(master, params.salt, params.rounds))


__all__ = ["KdfParams", "fernet_from_env"]
