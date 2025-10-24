#!/usr/bin/env python3
"""
Whalez-AI Runtime Health Verifier & Daily Discord Reporter
───────────────────────────────────────────────────────────
• Reads and summarizes logs from data/runtime_proofs.jsonl
• Computes uptime %, error rates, avg CPU & Memory load
• Sends a formatted health report to Discord webhook
"""

import json, os, statistics, datetime, requests

DATA_PATH = "data/runtime_proofs.jsonl"
WEBHOOK_URL = "https://discord.com/api/webhooks/1431119755837964352/KnU-IfJLehfiJZVqvKTPSLlVaq3GJdqBFeB-jYg7-lj1Cg0rVU04-rJPT00z052d-u3j"


def analyze_logs():
    """Read and summarize runtime proofs."""
    if not os.path.exists(DATA_PATH):
        return {"error": "No runtime proofs found."}

    with open(DATA_PATH) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    if not entries:
        return {"error": "No valid entries in log."}

    total = len(entries)
    errors = sum(1 for e in entries if e["status"] == "runtime_error")
    ok = sum(1 for e in entries if e["status"] == "runtime_ok")
    uptime = round((ok / total) * 100, 2)
    cpu = statistics.mean(e["metrics"]["cpu_percent"] for e in entries)
    mem = statistics.mean(e["metrics"]["memory_percent"] for e in entries)
    disk = statistics.mean(e["metrics"]["disk_usage_percent"] for e in entries)
    first = entries[0]["metrics"]["timestamp"]
    last = entries[-1]["metrics"]["timestamp"]

    return {
        "total": total,
        "errors": errors,
        "uptime": uptime,
        "cpu": cpu,
        "mem": mem,
        "disk": disk,
        "first": first,
        "last": last
    }


def send_discord_report(summary):
    """Post health summary to Discord webhook."""
    if "error" in summary:
        payload = {"content": f"⚠️ **Runtime Health Check Failed**\n{summary['error']}"}
    else:
        payload = {
            "content": (
                f"🩺 **Whalez-AI Daily Health Report**\n"
                f"──────────────────────────────\n"
                f"**Logs analyzed:** {summary['total']}\n"
                f"**Uptime:** {summary['uptime']}%\n"
                f"**Errors:** {summary['errors']}\n"
                f"**CPU Avg:** {summary['cpu']:.2f}%\n"
                f"**Memory Avg:** {summary['mem']:.2f}%\n"
                f"**Disk Usage:** {summary['disk']:.2f}%\n"
                f"**Period:** {summary['first']} → {summary['last']}\n"
                f"──────────────────────────────\n"
                f"✅ _Report generated automatically by Sentinel._"
            )
        }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
        print("[✔] Daily health report sent to Discord.")
    except Exception as e:
        print(f"[Webhook Error] {e}")


if __name__ == "__main__":
    summary = analyze_logs()
    send_discord_report(summary)
