import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line
from utils.rng import DummyRng
from config.build_config import build_test_config
from src.symbol import Symbol


def test_freespin_event():
    cfg = build_test_config(reels=[["A","B"]]*5, scatter="S")
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, s) for s in ["S","A","S","B","S"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)

    assert gs.free_spins >= 0
    assert any(ev["type"]=="freespin_update" for ev in result.get("events", []))
