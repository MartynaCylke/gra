import sys
import os
import pytest

# Dodaj src do sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from state.game_state import GameState
from calculations.lines import evaluate_single_line
from symbol import Symbol

# -----------------------------
# Dummy klasy potrzebne do testów
# -----------------------------

class DummyPaytable:
    def __init__(self):
        self.three_kind = {"A": 10, "B": 5, "C": 2}
        self.four_kind = {"A": 20, "B": 10, "C": 5}
        self.five_kind = {"A": 50, "B": 25, "C": 10}

class DummyCfg:
    def __init__(self):
        self.grid_width = 5
        self.grid_height = 3
        self.symbol_count = 10
        self.paytable = DummyPaytable()
        self.scatter_symbol = "S"
        self.other_setting = True
        self.special_symbols = {"wild": ["W"]}
        self.reels = 5
        self.mode = "normal"
        self.betmodes = [1]

dummy_cfg = DummyCfg()

class DummySymbol:
    def __init__(self, name):
        self.name = name

# -----------------------------
# Testy
# -----------------------------

def test_game_state_init():
    state = GameState(cfg=dummy_cfg)
    assert state is not None
    assert hasattr(state, "cfg")

def test_evaluate_single_line_example():
    line = [DummySymbol("A"), DummySymbol("B"), DummySymbol("C")]
    result = evaluate_single_line(line, cfg=dummy_cfg)
    assert result is not None

def test_game_state_run_spin():
    gs = GameState(cfg=dummy_cfg)
    board = [[DummySymbol("A")] for _ in range(dummy_cfg.reels)]
    gs.last_board = board

    class DummyRng:
        def __init__(self, values):
            self.values = values
            self.index = 0
        def next(self):
            val = self.values[self.index % len(self.values)]
            self.index += 1
            return val

    rng = DummyRng([col[0].name for col in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert result is not None
