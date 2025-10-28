import os, json

class LedgerAgent:
    def __init__(self, path="data/ledger.jsonl"):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                pass

    def count_blocks(self) -> int:
        if not os.path.exists(self.path): return 0
        with open(self.path, "r") as f:
            return sum(1 for _ in f)

    def refresh(self):
        os.makedirs("data", exist_ok=True)
        block = {"type": "ledger_sync", "ok": True}
        with open(self.path, "a") as f:
            f.write(json.dumps(block) + "\n")
        return {"count": self.count_blocks(), "issues": []}

