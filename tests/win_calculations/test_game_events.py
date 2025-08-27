import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line
from symbol.symbol import Symbol

# Prosty DummyRng do deterministycznych „losowań”
class DummyRng:
    def __init__(self, choices):
        self.choices = list(choices)
        self.i = 0
    def choice(self, _list):
        v = self.choices[self.i % len(self.choices)]
        self.i += 1
        return v
    def choice_weighted(self, seq, weights=None):
        return self.choice(seq)

# Lokalna, minimalna konfiguracja testowa z kompletną Paytable
def _cfg():
    class PT:
        def __init__(self):
            self.three_kind = {"A": 10, "B": 5, "C": 2}
            self.four_kind  = {"A": 20, "B": 10, "C": 4}
            self.five_kind  = {"A": 50, "B": 25, "C": 10}
    class CFG:
        mode = "lines"
        reels = [["A", "B", "C", "W", "S"]] * 5
        colors = ["A", "B", "C", "W", "S"]
        weights = None
        paytable = PT()
        special_symbols = {"wild": ["W"], "scatter": ["S"]}
        multiplier = None
    return CFG()

def test_spin_start_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True)
    board = [Symbol(cfg, s) for s in ["A", "A", "A", "B", "B"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert any(ev.get("type") == "spin_start" for ev in result.get("events", []))

def test_freespin_update_event():
    cfg = _cfg()
    gs = GameState(cfg, trace=True)
    # 3 scattery -> 10 freespinów, event freespin_update
    board = [Symbol(cfg, s) for s in ["S", "S", "S", "A", "B"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert gs.free_spins == 10
    assert any(ev.get("type") == "freespin_update" for ev in result.get("events", []))
