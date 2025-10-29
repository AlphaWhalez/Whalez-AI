import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_imports_ok():
    assert importlib.import_module("core.telemetry.streamer")
    assert importlib.import_module("core.voice.bridge")
    assert importlib.import_module("core.webui.routes")


def test_routes_registered():
    app = None
    for mod in ("api.gateway", "gateway", "main", "app"):
        try:
            m = importlib.import_module(mod)
            app = getattr(m, "app", None)
            if app:
                break
        except Exception:
            continue
    assert app is not None, "FastAPI app instance not found (api/gateway/main/app)"
    paths = {r.path for r in app.routes}
    assert "/console" in paths
    assert "/ws/stream" in paths
    assert "/ws/bridge" in paths
