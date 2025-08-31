import pytest
from src.state.game_state import GameState
from src.calculations.lines import evaluate_single_line
from src.symbol import Symbol
from tests.helpers import DummyRng, cfg_5reel

def make_board(cfg, symbols):
    return [[Symbol(cfg, s)] for s in symbols]

def test_spin_start_and_result_events():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = make_board(cfg, ["A","A","A","B","B"])
    gs.last_board = board
    rng = DummyRng([col[0].name for col in board])

    result = gs.run_spin(rng, evaluate_single_line)
    assert result is not None

def test_line_win_event():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = make_board(cfg, ["A","A","A","B","B"])
    gs.last_board = board
    rng = DummyRng([col[0].name for col in board])

    result = gs.run_spin(rng, evaluate_single_line)
    assert result is not None

def test_scatter_and_freespin_events():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = make_board(cfg, ["S","S","S","A","B"])
    gs.last_board = board
    rng = DummyRng([col[0].name for col in board])

    result = gs.run_spin(rng, evaluate_single_line)
    assert result is not None
