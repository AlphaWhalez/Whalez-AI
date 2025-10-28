"""
WADA (Whalez-Ai Domain Authority) Manager
- Hybrid mode: try Let's Encrypt; if not, fallback to Self-CA
- Writes certs to certs/live/<domain>/
"""
import os, socket, time, json
from pathlib import Path
from .signer import issue_server_cert
from .verify import cert_days_remaining, emit_log

DEFAULT_DOMAIN = os.getenv("WHALEZ_DOMAIN", "whalez-ai.local")
SETTINGS_PATH = Path("config/tls.settings.json")

def _load_settings():
    return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))

def _domain_resolves(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False

def ensure_certs(domain: str, settings: dict):
    cert_root = Path(settings["paths"]["cert_root"])
    log_file  = Path(settings["paths"]["log_file"])
    org       = settings["selfca"]["organization"]
    valid_days= int(settings["selfca"]["valid_days"])

    live_dir  = cert_root / "live" / domain
    crt_path  = live_dir / "fullchain.pem"
    key_path  = live_dir / "privkey.pem"
    chain_path= live_dir / "chain.pem"

    # If missing or near expiry, (re)issue via self-CA. (ACME hook can be added here later.)
    need_issue = (not crt_path.exists() or not key_path.exists())
    if not need_issue:
        days = cert_days_remaining(crt_path)
        if days <= settings["auto_rotate_days"]:
            need_issue = True

    if need_issue:
        crt_path, key_path, chain_path = issue_server_cert(domain, org, valid_days, cert_root)
        emit_log(Path(log_file), {
            "t": int(time.time()),
            "event": "cert_issued",
            "domain": domain,
            "mode": "self-ca",
            "paths": {"crt": str(crt_path), "key": str(key_path), "chain": str(chain_path)}
        })

    return crt_path, key_path

def main():
    settings = _load_settings()
    mode = settings.get("mode", "WADA-Hybrid")
    domain = os.getenv("WHALEZ_DOMAIN", DEFAULT_DOMAIN)

    # In Hybrid mode we *could* try ACME first if domain resolves publicly.
    # For now, we always ensure self-CA exists; ACME can be plugged here later.
    if mode in ("WADA-Hybrid", "WADA-Self"):
        if mode == "WADA-Hybrid" and _domain_resolves(domain):
            # TODO: place ACME issuance here; if fails → fallback self-CA
            pass

        crt_path, key_path = ensure_certs(domain, settings)
        return {
            "domain": domain,
            "cert": str(crt_path),
            "key": str(key_path),
            "host": settings["bind"]["host"],
            "https_port": settings["bind"]["https_port"],
            "http_redirect_port": settings["bind"]["http_redirect_port"],
        }

    raise SystemExit("Unsupported WADA mode")

if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
