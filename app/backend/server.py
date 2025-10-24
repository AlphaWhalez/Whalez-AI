#!/usr/bin/env python3
"""
Whalez-AI Backend API Gateway
──────────────────────────────
Bridges Sentinel + Agents to the Web & Mobile Apps
"""
from flask import Flask, jsonify
import json, os

app = Flask(__name__)

@app.route("/api/health")
def get_health():
    path = "data/runtime_proofs.jsonl"
    if not os.path.exists(path):
        return jsonify({"error": "No runtime logs yet"}), 404
    with open(path) as f:
        lines = f.readlines()[-10:]
    return jsonify({"recent_logs": [json.loads(l) for l in lines]})

@app.route("/api/ping")
def ping():
    return jsonify({"status": "Whalez-AI App Gateway online ✅"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
