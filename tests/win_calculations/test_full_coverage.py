import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line

from utils.rng import DummyRng
from config.build_config import build_test_config
from symbol.symbol import Symbol
from events.events import create_bonus_event


# ----------------- KONFIGURACJE -----------------

def cfg_5reel():
    return build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )


def cfg_3reel():
    return build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )


# ----------------- TESTY LINIOWE -----------------

@pytest.mark.parametrize(
    "board_symbols,expected_mult,expected_symbol,expected_count",
    [
        (["A", "A", "A", "B", "B"], 5, "A", 3),   # 3x "A"
        (["B", "B", "B", "A", "A"], 5, "B", 3),   # 3x "B"
        (["A", "A", "B", "A", "A"], 0, None, None), # niepełna wygrana
    ]
)
def test_line_win_various(board_symbols, expected_mult, expected_symbol, expected_count):
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    if expected_mult > 0:
        assert any(ev["type"] == "line_win" for ev in result.get("events", [])), "Brak eventu line_win"
    else:
        assert not any(ev["type"] == "line_win" for ev in result.get("events", []))


# ----------------- TESTY SCATTER I FREESPIN -----------------

@pytest.mark.parametrize(
    "board_symbols,expected_free_spins,scatter_expected",
    [
        (["S", "S", "S"], 10, True),      # 3 scatter → free spins
        (["S", "S", "A"], 0, False),      # 2 scatter → brak free spins
        (["A", "B", "C"], 0, False)       # 0 scatter → brak free spins
    ]
)
def test_scatter_freespin(board_symbols, expected_free_spins, scatter_expected):
    cfg = cfg_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    assert gs.free_spins == expected_free_spins
    scatter_ev_present = any(ev["type"] == "scatter_event" for ev in result.get("events", []))
    assert scatter_ev_present == scatter_expected
    freespin_ev_present = any(ev["type"] == "freespin_update" for ev in result.get("events", []))
    if expected_free_spins > 0:
        assert freespin_ev_present, "Brak eventu freespin_update"
    else:
        assert not freespin_ev_present


# ----------------- TESTY BONUSÓW -----------------

def test_bonus_event_added():
    cfg = cfg_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Tworzymy bonus
    create_bonus_event(gs, bonus_type="free_game", value=5)

    assert any(ev["type"] == "bonus_triggered" for ev in gs.book.get("events", [])), "Brak eventu bonus_triggered"


# ----------------- TESTY SPIN_START I SPIN_RESULT -----------------

def test_spin_start_and_result_events():
    cfg = cfg_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board_symbols = ["A", "A", "B"]
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    # Sprawdzenie, że zawsze pojawia się spin_start
    assert any(ev["type"] == "spin_start" for ev in result.get("events", [])), "Brak eventu spin_start"

    # Sprawdzenie, że spin_result też występuje
    assert any(ev["type"] == "spin_result" for ev in result.get("events", [])), "Brak eventu spin_result"
