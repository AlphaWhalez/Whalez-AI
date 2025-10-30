import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.intent import get_engine


def test_engine_enqueue_and_process():
    async def _run():
        engine = get_engine()
        intent = await engine.enqueue("unit-test", {"k": "v"})
        await asyncio.sleep(0.01)
        assert intent.status in {"running", "done"}
        await asyncio.sleep(0.01)
        assert intent.status == "done"

    asyncio.run(_run())
