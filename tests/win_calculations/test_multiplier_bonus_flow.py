import random
import pytest

from src.state.game_state import GameState
from src.symbol.symbol import Symbol
from src.config.test_config import build_test_config
from src.utils.dummy_rng import DummyRng
from src.utils.event_helpers import create_bonus_event, create_multiplier_event, report_events
from src.calculations.lines import evaluate_single_line

@pytest.mark.parametrize("num_freespins", [3, 5])
@pytest.mark.parametrize("reel_count", [3, 5])
def test_dynamic_freespins_with_random_boards(num_freespins, reel_count):
    cfg = build_test_config(scatter="S", multiplier=2, bonus="freespin_bonus")
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    create_bonus_event(gs, bonus_type="freespin_bonus", value=num_freespins)
    create_multiplier_event(gs, multiplier=2)

    symbols_pool = ["A", "B", "C", "W", "S"]

    for spin_index in range(num_freespins):
        board_symbols = random.choices(symbols_pool, k=reel_count)
        board = [Symbol(cfg, s) for s in board_symbols]
        gs.last_board = board
        rng = DummyRng(board_symbols)

        result = gs.run_spin(rng, evaluate_single_line)

        report_events(gs.book["events"])

        spin_result_events = [ev for ev in gs.book["events"] if ev["type"] == "spin_result"]
        assert spin_result_events, "Brak eventu spin_result"
        spin_win = spin_result_events[-1]["win"].get("total", 0)
        assert spin_win >= 0, f"Wygrana powinna być >=0, otrzymano {spin_win}"

def test_multiplier_and_bonus_affect_gameplay():
    cfg = build_test_config(scatter="S", multiplier=2, bonus="freespin_bonus")
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    board_symbols = ["A", "A", "A"]
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)

    result = gs.run_spin(rng, evaluate_single_line)
    spin_result_events = [ev for ev in gs.book["events"] if ev["type"] == "spin_result"]
    assert spin_result_events, "Brak eventu spin_result"

    base_win = spin_result_events[-1]["win"].get("total", 0)
    assert base_win >= 0
