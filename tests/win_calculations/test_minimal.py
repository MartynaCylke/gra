import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line
from tests.utils.dummy import DummyRng, build_test_config, Symbol


def test_freespin_event():
    cfg = build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )

    gs = GameState(cfg, trace=True, free_spins=3)
    gs.reset_book(criteria=cfg.mode)

    board = [
        Symbol(cfg, "S"),
        Symbol(cfg, "A"),
        Symbol(cfg, "S"),
        Symbol(cfg, "B"),
        Symbol(cfg, "S"),
    ]
    gs.last_board = board
    rng = DummyRng(["S", "A", "S", "B", "S"])

    result = gs.run_spin(rng, evaluate_single_line)

    assert gs.free_spins >= 0, "Free spins powinny być liczbą >= 0"
    assert any(ev["type"] == "freespin_event" for ev in result.get("events", [])), "Brak eventu freespin"
