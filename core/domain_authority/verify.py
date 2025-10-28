# Minimal cert validity + rotation checks
import datetime, json
from pathlib import Path
from cryptography import x509

def cert_days_remaining(cert_path: Path) -> int:
    cert = x509.load_pem_x509_certificate(cert_path.read_bytes())
    delta = cert.not_valid_after - datetime.datetime.utcnow().replace(tzinfo=cert.not_valid_after.tzinfo)
    return max(0, delta.days)

def emit_log(log_path: Path, event: dict):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
