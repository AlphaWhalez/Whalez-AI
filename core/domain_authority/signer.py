# Whalez-Ai Self-CA signer (cryptography)
import datetime
from pathlib import Path
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from typing import Tuple

def _write_pem(path: Path, key_or_cert, is_key=False, password: bytes = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    if is_key:
        enc = serialization.BestAvailableEncryption(password) if password else serialization.NoEncryption()
        pem = key_or_cert.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            enc
        )
    else:
        pem = key_or_cert.public_bytes(serialization.Encoding.PEM)
    path.write_bytes(pem)

def generate_self_ca(org: str, cert_root: Path) -> Tuple[Path, Path]:
    ca_key_path = cert_root / "selfca" / "root_ca.key.pem"
    ca_crt_path = cert_root / "selfca" / "root_ca.crt.pem"
    if ca_key_path.exists() and ca_crt_path.exists():
        return ca_crt_path, ca_key_path

    key = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, f"{org} Root CA"),
    ])
    now = datetime.datetime.utcnow()
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
        .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()), critical=False)
        .sign(private_key=key, algorithm=hashes.SHA256())
    )
    _write_pem(ca_key_path, key, is_key=True)
    _write_pem(ca_crt_path, cert, is_key=False)
    return ca_crt_path, ca_key_path

def issue_server_cert(domain: str, org: str, valid_days: int, cert_root: Path) -> Tuple[Path, Path, Path]:
    ca_crt, ca_key = generate_self_ca(org, cert_root)
    ca_key_obj = serialization.load_pem_private_key(ca_key.read_bytes(), password=None)
    ca_cert_obj = x509.load_pem_x509_certificate(ca_crt.read_bytes())

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = datetime.datetime.utcnow()
    subject = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, org),
        x509.NameAttribute(NameOID.COMMON_NAME, domain),
    ])
    san = x509.SubjectAlternativeName([x509.DNSName(domain)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert_obj.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=valid_days))
        .add_extension(san, critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(private_key=ca_key_obj, algorithm=hashes.SHA256())
    )

    live_dir = cert_root / "live" / domain
    key_path = live_dir / "privkey.pem"
    crt_path = live_dir / "fullchain.pem"
    ca_path  = live_dir / "chain.pem"

    _write_pem(key_path, key, is_key=True)
    _write_pem(crt_path, cert, is_key=False)
    _write_pem(ca_path, x509.load_pem_x509_certificate(ca_crt.read_bytes()), is_key=False)
    return crt_path, key_path, ca_path
