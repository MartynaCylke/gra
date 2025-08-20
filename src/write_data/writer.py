import json
from pathlib import Path
from typing import Dict, Any

class Writer:
    def __init__(self, out_dir: str):
        self.base = Path(out_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.f = (self.base / "events.jsonl").open("w", encoding="utf-8")

    def write(self, event: Dict[str, Any]):
        self.f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def close(self):
        self.f.close()
