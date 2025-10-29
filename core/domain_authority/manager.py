from pathlib import Path
import json, datetime
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa


class DomainAuthority:
    """Self-managed lightweight CA for preview & internal traffic."""

    def __init__(self, cfg_path="config/tls.settings.json"):
        self.cfg = json.load(open(cfg_path))
        self.store = Path(self.cfg["storage"]["dir"])
        self.store.mkdir(parents=True, exist_ok=True)
        self.ca_key = self.store / self.cfg["storage"]["ca_key"]
        self.ca_crt = self.store / self.cfg["storage"]["ca_cert"]

    def _new_key(self):
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def _subject(self, org, cn, country):
        return x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
            x509.NameAttribute(NameOID.COMMON_NAME, cn),
        ])

    def ensure_authority(self):
        if self.ca_key.exists() and self.ca_crt.exists():
            return
        key = self._new_key()
        subj = self._subject(self.cfg["authority"]["org"],
                             self.cfg["authority"]["common_name"],
                             self.cfg["authority"]["country"])
        now = datetime.datetime.utcnow()
        cert = (
            x509.CertificateBuilder()
            .subject_name(subj).issuer_name(subj)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=self.cfg["authority"]["valid_days"]))
            .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
            .sign(key, hashes.SHA256())
        )
        self.ca_key.write_bytes(
            key.private_bytes(serialization.Encoding.PEM,
                              serialization.PrivateFormat.TraditionalOpenSSL,
                              serialization.NoEncryption())
        )
        self.ca_crt.write_bytes(cert.public_bytes(serialization.Encoding.PEM))

    def issue_server_cert(self):
        """Issue/rotate a server cert signed by our CA."""
        self.ensure_authority()
        srv_key = self.store / self.cfg["storage"]["srv_key"]
        srv_crt = self.store / self.cfg["storage"]["srv_cert"]

        key = self._new_key()
        ca_key = serialization.load_pem_private_key(self.ca_key.read_bytes(), password=None)
        ca_crt = x509.load_pem_x509_certificate(self.ca_crt.read_bytes())

        now = datetime.datetime.utcnow()
        names = [x509.DNSName(n) for n in self.cfg["server"]["dns_names"]]
        subj = self._subject(self.cfg["authority"]["org"],
                             self.cfg["server"]["dns_names"][0],
                             self.cfg["authority"]["country"])
        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(subj)
            .add_extension(x509.SubjectAlternativeName(names), critical=False)
            .sign(key, hashes.SHA256())
        )
        cert = (
            x509.CertificateBuilder()
            .subject_name(csr.subject).issuer_name(ca_crt.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - datetime.timedelta(days=1))
            .not_valid_after(now + datetime.timedelta(days=self.cfg["server"]["valid_days"]))
            .add_extension(x509.SubjectAlternativeName(names), critical=False)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(private_key=ca_key, algorithm=hashes.SHA256())
        )

        srv_key.write_bytes(
            key.private_bytes(serialization.Encoding.PEM,
                              serialization.PrivateFormat.TraditionalOpenSSL,
                              serialization.NoEncryption())
        )
        srv_crt.write_bytes(cert.public_bytes(serialization.Encoding.PEM))

        return str(srv_key), str(srv_crt), str(self.ca_crt)
