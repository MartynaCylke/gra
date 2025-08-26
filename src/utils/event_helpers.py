def create_bonus_event(gs, bonus_type, value):
    gs.book.setdefault("events", []).append({"type": "bonus_triggered", "bonus_type": bonus_type, "value": value})

def create_multiplier_event(gs, multiplier):
    gs.book.setdefault("events", []).append({"type": "multiplier_update", "multiplier": multiplier})

def report_events(events):
    print("\n--- Event Coverage ---")
    counts = {}
    for ev in events:
        counts[ev["type"]] = counts.get(ev["type"], 0) + 1
    for k, v in counts.items():
        print(f"{k}: {v}")
    print("----------------------")
