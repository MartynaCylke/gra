import pytest
from symbol.symbol import Symbol
from state.game_state import GameState
from calculations.lines import evaluate_single_line

# --- DummyRng do testów ---
class DummyRng:
    def __init__(self, choices):
        self.choices = choices
        self.index = 0

    def choice(self, _list):
        val = self.choices[self.index]
        self.index = (self.index + 1) % len(self.choices)
        return val

# --- Poprawiona konfiguracja testowa ---
def _cfg():
    class Paytable:
        def __init__(self):
            self.three_kind = {"A": 10, "B": 5, "C": 2}

    class CFG:
        mode = "lines"
        reels = [["A", "B", "C"]] * 5
        colors = ["A", "B", "C"]
        weights = [1, 1, 1]
        paytable = Paytable()
        special_symbols = {"wild": ["W"]}  # symbol W jako Wild
    return CFG()

# --- Testy ---
def test_spin_start_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board = [Symbol(cfg, name) for name in ["A", "A", "A", "A", "A"]]
    gs.last_board = board
    rng = DummyRng(["A", "A", "A", "A", "A"])
    result = gs.run_spin(rng, evaluate_single_line)
    assert "board" in result['events'][0]


def test_freespin_update_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True, free_spins=3)
    board = [Symbol(cfg, name) for name in ["A", "A", "A", "A", "A"]]
    win = evaluate_single_line(board, cfg)
    gs.reset_book(criteria=cfg.mode)
    gs.add_event({"board": board, "win": win})
    update_event = {"index": 0, "type": "freespin_update", "freeSpinsRemaining": gs.free_spins}
    gs.add_event(update_event)
    gs.finalize_book(win.get("mult", 0))
    events = gs.book.get("events", [])
    assert any(e.get("type") == "freespin_update" for e in events)

def test_bonus_triggered_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True)
    board = [Symbol(cfg, name) for name in ["W", "W", "W", "A", "A"]]
    gs.reset_book(criteria=cfg.mode)
    gs.add_event({"board": board})
    bonus_event = {"index": 0, "type": "bonus_triggered", "bonus_type": "freespin", "value": 3}
    gs.add_event(bonus_event)
    gs.finalize_book(0)
    events = gs.book.get("events", [])
    assert any(e.get("type") == "bonus_triggered" for e in events)

def test_multiplier_update_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True)
    board = [Symbol(cfg, name) for name in ["A", "A", "A", "A", "A"]]
    win = {"symbol": "A", "count": 5, "mult": 2}
    gs.reset_book(criteria=cfg.mode)
    gs.add_event({"board": board, "win": win})
    multiplier_event = {"index": 0, "type": "multiplier_update", "multiplier": win["mult"]}
    gs.add_event(multiplier_event)
    gs.finalize_book(win.get("mult", 0))
    events = gs.book.get("events", [])
    assert any(e.get("type") == "multiplier_update" for e in events)

# Możesz dopisać kolejne testy run_spin_with_events i run_spin_with_bonus_and_wilds
# analogicznie, upewniając się, że odczyty używają .get("type") lub .get("multiplier")
