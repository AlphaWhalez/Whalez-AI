import os, json, time
from typing import Dict

AUDIT = "data/reward_proofs.jsonl"
os.makedirs("data", exist_ok=True)

DEFAULT_WEIGHTS = {
    "founder": 1.0,
    "whalez_ai_core": 0.6,
    "head_coaches": 0.4,
    "vip_users": 0.3,
    "sub_model_ais": 0.2,
    "validator_council": 0.15,
    "general_users": 0.1
}

def _emit_proof(record: Dict):
    with open(AUDIT, "a") as f:
        f.write(json.dumps(record) + "\n")

def preview_allocation(total_pltr: float, performance: Dict[str, float]) -> Dict[str, float]:
    scores = {}
    for k, w in DEFAULT_WEIGHTS.items():
        p = performance.get(k, 1.0)
        scores[k] = max(0.0, w * p)
    total_score = sum(scores.values()) or 1.0
    return {k: round(total_pltr * (v / total_score), 6) for k, v in scores.items()}

def payout(total_pltr: float, performance: Dict[str, float], initiator: str = "system"):
    alloc = preview_allocation(total_pltr, performance)
    ts = int(time.time())
    _emit_proof({
        "ts": ts,
        "type": "proof_of_reward",
        "amount": total_pltr,
        "alloc": alloc,
        "performance": performance,
        "initiator": initiator
    })
    return {"ts": ts, "alloc": alloc, "tx_status": "recorded_stub"}

