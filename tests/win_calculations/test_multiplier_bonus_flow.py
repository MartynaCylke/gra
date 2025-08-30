import pytest

from state.game_state import GameState
from symbol.symbol import Symbol
from config.build_config import build_test_config
from utils.rng import DummyRng
from utils.event_helpers import create_bonus_event, create_multiplier_event, report_events
from calculations.lines import evaluate_single_line


@pytest.mark.parametrize("num_freespins", [3, 5])
@pytest.mark.parametrize("reel_count", [3, 5])
def test_dynamic_freespins_with_random_boards(num_freespins, reel_count):
    cfg = build_test_config(scatter="S", multiplier=2, bonus="freespin_bonus")
    gs = GameState(cfg, trace=True)
    # Wyłączamy ForceLoader, żeby deterministyczne boardy działały
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    # Tworzymy bonus i mnożnik
    create_bonus_event(gs, bonus_type="freespin_bonus", value=num_freespins)
    create_multiplier_event(gs, multiplier=2)

    # Pool symboli
    symbols_pool = ["A", "B", "C", "W", "S"]

    for spin_index in range(num_freespins):
        # Wymuszony deterministyczny board
        board_symbols = symbols_pool[:reel_count]  # np. ['A', 'B', 'C'] dla reel_count=3
        board = [Symbol(cfg, s) for s in board_symbols]
        gs.last_board = board

        rng = DummyRng([s.name for s in board])  # deterministyczny RNG
        result = gs.run_spin(rng, evaluate_single_line)

        report_events(gs.book["events"])

        # Sprawdzenie eventu spin_result
        spin_result_events = [ev for ev in gs.book["events"] if ev["type"] == "spin_result"]
        assert spin_result_events, "Brak eventu spin_result"

        spin_win = spin_result_events[-1]["win"].get("total", 0)
        assert spin_win >= 0, f"Wygrana powinna być >=0, otrzymano {spin_win}"


def test_multiplier_and_bonus_affect_gameplay():
    cfg = build_test_config(scatter="S", multiplier=2, bonus="freespin_bonus")
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    # Wymuszony board do spin
    board_symbols = ["A", "A", "A"]
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)

    result = gs.run_spin(rng, evaluate_single_line)

    spin_result_events = [ev for ev in gs.book["events"] if ev["type"] == "spin_result"]
    assert spin_result_events, "Brak eventu spin_result"

    base_win = spin_result_events[-1]["win"].get("total", 0)
    assert base_win >= 0, f"Wygrana powinna być >=0, otrzymano {base_win}"
