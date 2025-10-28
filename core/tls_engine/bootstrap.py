"""
Bootstrap secure serving:
- Ensures certs exist (via WADA manager)
- Starts HTTPS Flask gateway on configured port with SSL context
- Optional HTTP→HTTPS redirect helper (separate process/terminal if desired)
"""
import os, ssl, sys
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.domain_authority.manager import main as wada_main
from api.gateway import app as flask_app

def run():
    cfg = wada_main()  # ensures certs; returns paths + bind info
    cert_path = cfg["cert"]
    key_path  = cfg["key"]
    host      = cfg["host"]
    port      = int(cfg["https_port"])

    os.environ["PORT"] = str(port)  # keep gateway introspection coherent

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    print(f"🔐 Whalez-AI HTTPS: https://{host}:{port}")
    print(f"⭐ Using cert: {cert_path}")
    flask_app.run(host=host, port=port, ssl_context=context)

if __name__ == "__main__":
    run()
