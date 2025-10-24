#!/usr/bin/env python3
"""
Runtime Proof Verifier for Whalez-AI
────────────────────────────────────
Reads data/runtime_proofs.jsonl and summarizes system stability:
 - total proofs logged
 - uptime percentage
 - runtime_error count
 - average CPU and memory load
"""

import json, os, statistics, datetime

DATA_PATH = "data/runtime_proofs.jsonl"

def analyze_logs():
    if not os.path.exists(DATA_PATH):
        print("⚠️ No runtime proofs found.")
        return

    with open(DATA_PATH) as f:
        entries = [json.loads(line) for line in f if line.strip()]

    if not entries:
        print("⚠️ No valid entries found.")
        return

    total = len(entries)
    errors = sum(1 for e in entries if e["status"] == "runtime_error")
    ok = sum(1 for e in entries if e["status"] == "runtime_ok")
    uptime = round((ok / total) * 100, 2)
    cpu = statistics.mean(e["metrics"]["cpu_percent"] for e in entries)
    mem = statistics.mean(e["metrics"]["memory_percent"] for e in entries)

    first = entries[0]["metrics"]["timestamp"]
    last = entries[-1]["metrics"]["timestamp"]

    print("📊 Whalez-AI Runtime Health Summary")
    print("───────────────────────────────────")
    print(f"Logs analyzed: {total}")
    print(f"Uptime: {uptime}%")
    print(f"Errors: {errors}")
    print(f"Avg CPU: {cpu:.2f}%")
    print(f"Avg Memory: {mem:.2f}%")
    print(f"Period: {first} → {last}")

if __name__ == "__main__":
    analyze_logs()
