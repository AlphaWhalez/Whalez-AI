from pathlib import Path
import json


class AffirmationCore:
    def __init__(self, schema_path="config/world.schema.json"):
        self.schema_path = Path(schema_path)
        self.world = {}

    def load(self):
        if self.schema_path.exists():
            with open(self.schema_path, "r", encoding="utf-8") as f:
                self.world = json.load(f)
        return self.world

    def get_founder(self):
        return self.world.get("world", {}).get("founder", {})

    def describe(self):
        founder = self.get_founder()
        return f"Whalez-World initialized. Founder: {founder.get('display_name', 'Unknown')}"
