from src.config.build_config import GameConfig, Paytable
from src.calculations.lines import evaluate_single_line
from src.symbol import Symbol


def _cfg():
    """
    Konfiguracja testowa z pełnym paytable (3oak, 4oak, 5oak).
    Dzięki temu testy 5-bębnowe nie walą KeyError.
    """
    return GameConfig(
        id="t",
        mode="lines",
        bet=1,
        reels=[[], [], []],
        paytable=Paytable(
            three_kind={"A": 5, "K": 4, "Q": 3, "J": 2},
            four_kind={"A": 10, "K": 8, "Q": 6, "J": 4},
            five_kind={"A": 20, "K": 16, "Q": 12, "J": 8},
        ),
        special_symbols={"wild": ["W"]},  # symbol Wild
    )


# ----------------- TESTY 3-BĘBNOWE -----------------

def test_3oak_A_wins():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["A", "A", "A"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 5
    assert win["symbol"] == "A"
    assert win["count"] == 3


def test_3oak_K_wins():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["K", "K", "K"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 4
    assert win["symbol"] == "K"
    assert win["count"] == 3


def test_wild_substitution():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["W", "A", "A"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 5
    assert win["symbol"] == "A"
    assert win["count"] == 3


def test_no_win():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["A", "K", "Q"]]
    win = evaluate_single_line(board, cfg)
    assert win == {}


def test_mixed_wilds():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["W", "W", "A"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 5
    assert win["symbol"] == "A"
    assert win["count"] == 3


def test_partial_win():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["A", "A", "K"]]
    win = evaluate_single_line(board, cfg)
    assert win == {}


# ----------------- TESTY 5-BĘBNOWE -----------------

def test_5oak_A_wins():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["A", "A", "A", "A", "A"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 20
    assert win["symbol"] == "A"
    assert win["count"] == 5


def test_5oak_with_wilds():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["W", "A", "W", "A", "A"]]
    win = evaluate_single_line(board, cfg)
    assert win["mult"] == 20
    assert win["symbol"] == "A"
    assert win["count"] == 5


def test_no_win_5b():
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["A", "K", "Q", "J", "K"]]
    win = evaluate_single_line(board, cfg)
    assert win == {}
