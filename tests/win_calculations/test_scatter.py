# tests/win_calculations/test_scatter.py

import sys
import os

# Dodaj src do sys.path, żeby Python widział pakiety
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from state.game_state import GameState
from calculations.lines import evaluate_single_line

# -----------------------------
# Dummy klasy potrzebne do testów
# -----------------------------

class DummyPaytable:
    """Dummy paytable, który symuluje strukturę używaną w funkcjach"""
    def __init__(self):
        self.three_kind = [0, 1, 2]
        self.four_kind = [0, 0, 0]
        self.five_kind = [0, 0, 0]

class DummyCfg:
    """Dummy konfiguracja, żeby testy przechodziły"""
    def __init__(self):
        self.grid_width = 5
        self.grid_height = 3
        self.symbol_count = 10
        self.paytable = DummyPaytable()
        self.scatter_symbol = "S"
        self.other_setting = True
        self.special_symbols = {"wild": ["W"]}

# Jeden obiekt dummy_cfg używany we wszystkich testach
dummy_cfg = DummyCfg()

class DummySymbol:
    """Dummy symbol, który ma atrybut 'name' wymagany przez evaluate_single_line"""
    def __init__(self, name):
        self.name = name

# -----------------------------
# Testy
# -----------------------------

def test_game_state_init():
    """Test inicjalizacji GameState z dummy_cfg"""
    state = GameState(cfg=dummy_cfg)
    assert state is not None
    assert hasattr(state, "cfg")

def test_evaluate_single_line_example():
    """Test funkcji evaluate_single_line z dummy_cfg i dummy-symbolami"""
    # Tworzymy listę dummy-symboli
    line = [DummySymbol("A"), DummySymbol("B"), DummySymbol("C")]
    result = evaluate_single_line(line, cfg=dummy_cfg)
    assert result is not None
