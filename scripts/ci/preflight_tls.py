from core.tls_engine.bootstrap import ensure_tls_artifacts
from core.domain_authority.verify import CertVerifier

art = ensure_tls_artifacts()
with open(art["cert"], "rb") as f:
    assert CertVerifier.sanity(f.read())
print('{"ok": true}')
