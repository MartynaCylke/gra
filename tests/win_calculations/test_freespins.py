from src.state.game_state import GameState
from src.calculations.lines import evaluate_single_line
from src.symbol import Symbol
from tests.helpers import DummyRng, build_test_config

def make_board(cfg, symbols):
    return [[Symbol(cfg, s)] for s in symbols]

def test_freespin_event():
    cfg = build_test_config(reels=[["A","B"]] * 5, scatter="S")
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = make_board(cfg, ["S","A","S","B","S"])
    gs.last_board = board
    rng = DummyRng([col[0].name for col in board])

    result = gs.run_spin(rng, evaluate_single_line)
    assert result is not None
