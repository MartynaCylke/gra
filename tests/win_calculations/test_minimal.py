import pytest
from src.state.game_state import GameState
from src.symbol.symbol import Symbol
from src.utils.rng import DummyRng
from src.config.build_config import build_test_config
from src.calculations.lines import evaluate_single_line

# ------------------ Test 1: Linie podstawowe ------------------
def test_basic_line_win():
    cfg = build_test_config(
        reels=[["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"], ["A", "B", "C"]]
    )
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, "A") for _ in range(5)]
    gs.last_board = board
    rng = DummyRng(["A"]*5)

    result = gs.run_spin(rng, evaluate_single_line)

    assert any(ev["type"] == "spin_result" for ev in result["events"]), "Brak spin_result"
    assert result["baseGameWins"] >= 0

# ------------------ Test 2: Scatter triggers free spins ------------------
def test_scatter_triggers_free_spins():
    cfg = build_test_config(
        reels=[["S", "A", "B"], ["S", "A", "B"], ["S", "A", "B"], ["S", "A", "B"], ["S", "A", "B"]],
        scatter="S"
    )
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, "S"), Symbol(cfg, "S"), Symbol(cfg, "S"), Symbol(cfg, "A"), Symbol(cfg, "B")]
    gs.last_board = board
    rng = DummyRng(["S", "S", "S", "A", "B"])

    result = gs.run_spin(rng, evaluate_single_line)

    assert result.get("scatterWins", 0) > 0, "Scatter powinien generować wygraną"
    assert gs.free_spins >= 10, "Powinno dodać darmowe spiny"
    assert any(ev["type"] == "scatter_event" for ev in result["events"]), "Brak scatter_event"

# ------------------ Test 3: Free spins event ------------------
def test_freespin_event():
    cfg = build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, "A"), Symbol(cfg, "A"), Symbol(cfg, "B"), Symbol(cfg, "B"), Symbol(cfg, "A")]
    gs.last_board = board
    rng = DummyRng(["A", "A", "B", "B", "A"])

    result = gs.run_spin(rng, evaluate_single_line)

    assert gs.free_spins >= 0, "Free spins powinny być liczbą >= 0"
    assert any(ev["type"] == "freespin_event" for ev in result.get("events", [])), "Brak eventu freespin"
