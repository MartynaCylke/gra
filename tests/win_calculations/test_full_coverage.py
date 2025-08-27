import pytest
from src.symbol.symbol import Symbol
from state.game_state import GameState
from src.utils.dummy_rng import DummyRng
from src.calculations.lines import evaluate_single_line
from tests.conftest import cfg_5reel, cfg_3reel
from events.events import create_bonus_event

# ----------------- TESTY LINIOWE -----------------
@pytest.mark.parametrize(
    "board_symbols,expected_mult,expected_symbol,expected_count",
    [
        (["A", "A", "A", "B", "B"], 10, "A", 3),   # 3x "A"
        (["B", "B", "B", "A", "A"], 5, "B", 3),    # 3x "B"
        (["A", "A", "B", "A", "A"], 20, "A", 4),   # 4x "A"
        (["A", "B", "A", "B", "C"], 0, None, None),# brak pełnej wygranej
    ]
)
def test_line_win_various(cfg_5reel, board_symbols, expected_mult, expected_symbol, expected_count):
    cfg = cfg_5reel
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    if expected_mult > 0:
        lwins = [ev for ev in result.get("events", []) if ev["type"] == "line_win"]
        assert lwins, "Brak eventu line_win"
        ev = lwins[0]
        assert ev["mult"] == expected_mult
        assert ev["symbol"] == expected_symbol
        assert ev["count"] == expected_count
    else:
        assert not any(ev["type"] == "line_win" for ev in result.get("events", []))

# ----------------- TESTY SCATTER I FREESPIN -----------------
@pytest.mark.parametrize(
    "board_symbols,expected_free_spins,scatter_expected",
    [
        (["S", "S", "S"], 10, True),  # 3 scatter → free spins
        (["S", "S", "A"], 0, False),  # 2 scatter → brak free spins
        (["A", "B", "C"], 0, False)   # 0 scatter → brak free spins
    ]
)
def test_scatter_freespin(cfg_3reel, board_symbols, expected_free_spins, scatter_expected):
    cfg = cfg_3reel
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
def test_bonus_event_added(cfg_3reel):
    cfg = cfg_3reel
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    create_bonus_event(gs, bonus_type="free_game", value=5)
    assert any(ev["type"] == "bonus_triggered" for ev in gs.book.get("events", [])), "Brak eventu bonus_triggered"

# ----------------- TESTY SPIN_START I SPIN_RESULT -----------------
def test_spin_start_and_result_events(cfg_3reel):
    cfg = cfg_3reel
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board_symbols = ["A", "A", "B"]
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    assert any(ev["type"] == "spin_start" for ev in result.get("events", [])), "Brak eventu spin_start"
    assert any(ev["type"] == "spin_result" for ev in result.get("events", [])), "Brak eventu spin_result"

# ----------------- TESTY WILD -----------------
@pytest.mark.parametrize(
    "board_symbols,expected_mult,expected_symbol,expected_count",
    [
        (["W", "A", "A", "A", "A"], 50, "A", 5),   # 4x A + 1 Wild = 5x A → mult=50
        (["W", "W", "A", "B", "B"], 10, "B", 4),   # 2x B + 2 Wild = 4x B → mult=10
        (["W", "W", "W", "A", "A"], 50, "A", 5),   # 2x A + 3 Wild = 5x A → mult=50
    ]
)
def test_wild_substitution(cfg_5reel, board_symbols, expected_mult, expected_symbol, expected_count):
    cfg = cfg_5reel
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    lwins = [ev for ev in result.get("events", []) if ev["type"] == "line_win"]
    assert lwins, "Brak eventu line_win"
    ev = lwins[0]
    assert ev["mult"] == expected_mult
    assert ev["symbol"] == expected_symbol
    assert ev["count"] == expected_count
