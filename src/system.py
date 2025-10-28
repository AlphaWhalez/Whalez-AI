import time, json, socket, psutil
from typing import Dict

def system_status_snapshot(ledger_agent) -> Dict:
    return {
        "hostname": socket.gethostname(),
        "uptime_sec": int(time.time() - psutil.boot_time()),
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_mb": int(psutil.virtual_memory().used / 1024 / 1024),
        "ledger_indexed": ledger_agent.count_blocks(),
        "ts": int(time.time())
    }

def verify_system_integrity(ledger_agent) -> Dict:
    issues = []
    if ledger_agent.count_blocks() < 0:
        issues.append("negative_block_count")
    return {"status": "ok" if not issues else "warn", "issues": issues}

