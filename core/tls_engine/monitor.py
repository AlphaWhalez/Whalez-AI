# Simple long-running monitor (optional): re-issues near expiry
import time
from core.domain_authority.manager import ensure_certs, _load_settings

def loop(domain: str):
    settings = _load_settings()
    while True:
        ensure_certs(domain, settings)
        time.sleep(6 * 60 * 60)  # every 6 hours

if __name__ == "__main__":
    domain = "whalez-ai.local"
    loop(domain)
