# very small health probes wrapper used by the recovery agent
from __future__ import annotations
import subprocess, shlex
from typing import Tuple

def check_cmd(cmd: str, timeout: int = 20) -> Tuple[bool, str]:
    try:
        proc = subprocess.run(shlex.split(cmd), capture_output=True, timeout=timeout)
        ok = proc.returncode == 0
        out = (proc.stdout or proc.stderr).decode("utf-8", errors="ignore")
        return ok, out.strip()
    except Exception as e:
        return False, f"probe-error: {e}"
