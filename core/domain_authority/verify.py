from cryptography import x509


class CertVerifier:
    @staticmethod
    def sanity(server_cert_pem: bytes):
        # minimal parse check
        x509.load_pem_x509_certificate(server_cert_pem)
        return True
