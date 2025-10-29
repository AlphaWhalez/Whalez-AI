from core.domain_authority import CertificateSigner
from pathlib import Path


def ensure_tls_artifacts():
    key, crt, ca = CertificateSigner().ensure()
    for p in (key, crt, ca):
        assert Path(p).exists(), f"missing {p}"
    return {"key": key, "cert": crt, "ca": ca}
