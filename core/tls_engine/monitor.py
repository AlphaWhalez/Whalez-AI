from pathlib import Path


def tls_status(store=".secrets/tls"):
    store = Path(store)
    ok = all([
        (store / "ca.cert.pem").exists(),
        (store / "server.cert.pem").exists(),
        (store / "server.key.pem").exists(),
    ])
    return {"tls_ok": bool(ok)}
