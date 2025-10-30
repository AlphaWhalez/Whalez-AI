from nacl import signing
from nacl.encoding import HexEncoder
import hashlib
import json
import os


def canonical(obj) -> bytes:
    """Deterministic JSON bytes for signing/hashing."""
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_or_create_node_key(path: str = ".node_ed25519.key") -> signing.SigningKey:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return signing.SigningKey(f.read())
    sk = signing.SigningKey.generate()
    with open(path, "wb") as f:
        f.write(bytes(sk))
    return sk


def sign_dict(sk: signing.SigningKey, payload: dict) -> dict:
    msg = canonical(payload)
    sig = sk.sign(msg).signature.hex()
    vk_hex = sk.verify_key.encode(encoder=HexEncoder).decode()
    return {"payload": payload, "hash": sha256(msg), "sig": sig, "pub": vk_hex}


def verify_signed(signed: dict) -> bool:
    payload = signed["payload"]
    signature = bytes.fromhex(signed["sig"])
    msg = canonical(payload)
    if sha256(msg) != signed["hash"]:
        return False
    vk = signing.VerifyKey(bytes.fromhex(signed["pub"]))
    vk.verify(msg, signature)  # raises if invalid
    return True
