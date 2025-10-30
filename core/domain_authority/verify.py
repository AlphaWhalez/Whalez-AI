try:  # pragma: no cover - optional dependency for lightweight environments
    from cryptography import x509
    _HAS_CRYPTO = True
except Exception:  # pragma: no cover
    x509 = None  # type: ignore
    _HAS_CRYPTO = False


class CertVerifier:
    @staticmethod
    def sanity(server_cert_pem: bytes):
        if not _HAS_CRYPTO:
            raise RuntimeError("cryptography package is required for TLS verification")
        # minimal parse check
        x509.load_pem_x509_certificate(server_cert_pem)
        return True
