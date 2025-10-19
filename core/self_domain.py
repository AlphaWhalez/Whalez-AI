"""Deterministic Whalez subdomain calculation utilities."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict

from .affirmation_core import WhalezIdentity, AffirmationCore


def deterministic_subdomain(identity: WhalezIdentity | Dict[str, str]) -> str:
    """Return a deterministic subdomain derived from the identity.

    The founder hash is hashed again with the domain seed to ensure that the
    resulting value is stable yet non-trivial to guess.
    """

    if isinstance(identity, WhalezIdentity):
        founder_hash = identity.founder_hash
        seed = identity.domain_seed
    else:
        founder_hash = identity["founder_hash"]
        seed = identity["domain_seed"]

    digest = hashlib.sha256(f"{founder_hash}:{seed}".encode("utf-8")).hexdigest()
    return f"{digest[:12]}.{seed}"


def record_subdomain(core: AffirmationCore) -> str:
    """Record the current subdomain calculation in the affirmation log."""

    subdomain = deterministic_subdomain(core.identity)
    core.append("Calculated deterministic subdomain", {"subdomain": subdomain})
    return subdomain


def identity_path_default() -> Path:
    """Return the default identity path for convenience APIs."""

    return Path("core/whalez_identity.json")


__all__ = ["deterministic_subdomain", "record_subdomain", "identity_path_default"]
