from src.config.build_config import GameConfig, Paytable
from src.calculations.lines import evaluate_single_line

def _cfg():
    return GameConfig(
        id="t",
        mode="lines",
        bet=1,
        reels=[[], [], []],
        paytable=Paytable(three_kind={"A": 5, "K": 4, "Q": 3, "J": 2}),
    )

def test_3oak_A_wins():
    board = ["A", "A", "A"]
    win = evaluate_single_line(board, _cfg())
    assert win["mult"] == 5

def test_wild_substitution():
    board = ["W", "A", "A"]
    win = evaluate_single_line(board, _cfg())
    assert win["mult"] == 5

def test_no_win():
    board = ["A", "K", "Q"]
    win = evaluate_single_line(board, _cfg())
    assert win == {}
