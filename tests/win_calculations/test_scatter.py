# tests/win_calculations/test_scatter.py

import sys
import os
import pytest

# Dodajemy src do sys.path, żeby Python widział moduły
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Importy z pakietu calculations
from calculations.lines import evaluate_single_line
from calculations.game_state import GameState


def test_evaluate_single_line():
    line = [1, 2, 3]
    result = evaluate_single_line(line)
    assert result is not None  # dostosuj do rzeczywistej logiki funkcji


def test_game_state_initialization():
    game = GameState()
    assert isinstance(game, GameState)
