import json
from pathlib import Path


class ForceLoader:
    def __init__(self, filepath="force.json"):
        self.filepath = Path(filepath)
        self.events = []
        self.index = 0
        self.enabled = False

        if self.filepath.exists():
            with open(self.filepath, "r") as f:
                self.events = json.load(f)
            if self.events:
                self.enabled = True
                print(f"[ForceLoader] Załadowano {len(self.events)} zdarzeń z {self.filepath}")

    def next_event(self):
        if not self.enabled:
            return None
        if self.index >= len(self.events):
            print("[ForceLoader] Wszystkie eventy zostały wykorzystane.")
            return None
        event = self.events[self.index]
        self.index += 1
        return event
