import os
import asyncio
from .models import Intent
from core.telemetry.streamer import TelemetryStreamer

DRY_RUN = os.getenv("DRY_RUN", "1") == "1"


# --- Handler: DNS Mint (Phase-H runner) ---------------------------------------
async def dns_mint(intent: Intent, streamer: TelemetryStreamer = None):
    """
    Uses the Phase-H script contract. We *simulate* by writing an audit record.
    Real call should shell out to scripts/deploy_autonomous_dns.py when DRY_RUN=0.
    """
    await asyncio.sleep(0)  # yield control
    sub = intent.payload.get("sub", "ai")
    audit = {
        "action": "dns_mint",
        "sub": sub,
        "domain": f"{sub}.deltaalpha-trade-pro.com",
        "dry_run": DRY_RUN,
    }
    if streamer:
        streamer.emit("dns.mint.audit", audit)
    if DRY_RUN:
        # simulate success
        return {"status": "simulated", **audit}
    # Real path (kept inert unless DRY_RUN=0)
    # import subprocess, sys
    # subprocess.check_call([sys.executable, "scripts/deploy_autonomous_dns.py"])
    return {"status": "executed", **audit}


# --- Handler: Console command --------------------------------------------------
async def console_cmd(intent: Intent, streamer: TelemetryStreamer = None):
    await asyncio.sleep(0)
    cmd = intent.payload.get("cmd", "noop")
    record = {"action": "console_cmd", "cmd": cmd}
    if streamer:
        streamer.emit("console.cmd.audit", record)
    return {"status": "ack", **record}
