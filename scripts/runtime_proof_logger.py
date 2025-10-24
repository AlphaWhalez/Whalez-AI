#!/usr/bin/env python3
"""
Whalez-AI Runtime Proof Logger
──────────────────────────────
• Collects real-time system metrics (CPU, RAM, Disk)
• Saves continuous health snapshots to /data/runtime_proofs.jsonl
• Sends every proof event to a private Discord webhook
"""

import os, json, psutil, time, datetime, requests

# === CONFIG ===
DATA_PATH = "data/runtime_proofs.jsonl"
WEBHOOK_URL = "https://discord.com/api/webhooks/1431119755837964352/KnU-IfJLehfiJZVqvKTPSLlVaq3GJdqBFeB-jYg7-lj1Cg0rVU04-rJPT00z052d-u3j"

# Ensure directory exists
os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)


def collect_metrics():
    """Collect system metrics snapshot."""
    return {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage_percent": psutil.disk_usage("/").percent,
        "active_processes": len(psutil.pids()),
    }


def send_discord_notification(entry):
    """Send the proof entry to the Discord webhook."""
    try:
        payload = {
            "content": (
                f"📡 **Whalez-AI Runtime Proof**\n"
                f"Status: `{entry['status']}`\n"
                f"Note: {entry['note']}\n"
                f"CPU: {entry['metrics']['cpu_percent']}% | "
                f"Memory: {entry['metrics']['memory_percent']}% | "
                f"Disk: {entry['metrics']['disk_usage_percent']}%\n"
                f"Processes: {entry['metrics']['active_processes']}\n"
                f"Time: {entry['metrics']['timestamp']}"
            )
        }
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except Exception as e:
        print(f"[Webhook Error] {e}")


def log_event(status, note=""):
    """Record an event both locally and remotely."""
    entry = {"status": status, "note": note, "metrics": collect_metrics()}
    try:
        with open(DATA_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[Proof] Logged: {status} — {note}")
        send_discord_notification(entry)
    except Exception as e:
        print(f"[Log Error] {e}")


if __name__ == "__main__":
    log_event("runtime_start", "Sentinel logging initialized")
    while True:
        try:
            log_event("runtime_ok", "System stable")
            time.sleep(60)
        except Exception as e:
            log_event("runtime_error", str(e))
            time.sleep(10)
