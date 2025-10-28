import hashlib


def deterministic_subdomain(seed: str) -> str:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]
    return f"whalez-{h}"
