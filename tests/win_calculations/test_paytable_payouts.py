import pytest
from src.config.build_config import GameConfig, Paytable
from src.calculations.lines import evaluate_single_line
from src.symbol import Symbol



def _cfg():
    """
    Konfiguracja z pełnym paytable do testów wypłat.
    """
    return GameConfig(
        id="payout",
        mode="lines",
        bet=1,
        reels=[[], [], [], [], []],
        paytable=Paytable(
            three_kind={"A": 10, "K": 8, "Q": 6, "J": 4},
            four_kind={"A": 20, "K": 16, "Q": 12, "J": 8},
            five_kind={"A": 50, "K": 40, "Q": 30, "J": 20},
        ),
        special_symbols={"wild": ["W"]},
    )


@pytest.mark.parametrize(
    "board,expected_symbol,expected_count,expected_mult",
    [
        # 3oak
        (["A", "A", "A"], "A", 3, 10),
        (["K", "K", "K"], "K", 3, 8),
        (["Q", "Q", "Q"], "Q", 3, 6),
        (["J", "J", "J"], "J", 3, 4),

        # 4oak
        (["A", "A", "A", "A"], "A", 4, 20),
        (["K", "K", "K", "K"], "K", 4, 16),
        (["Q", "Q", "Q", "Q"], "Q", 4, 12),
        (["J", "J", "J", "J"], "J", 4, 8),

        # 5oak
        (["A", "A", "A", "A", "A"], "A", 5, 50),
        (["K", "K", "K", "K", "K"], "K", 5, 40),
        (["Q", "Q", "Q", "Q", "Q"], "Q", 5, 30),
        (["J", "J", "J", "J", "J"], "J", 5, 20),
    ]
)
def test_paytable_payouts(board, expected_symbol, expected_count, expected_mult):
    cfg = _cfg()
    symbols = [Symbol(cfg, s) for s in board]
    win = evaluate_single_line(symbols, cfg)

    assert win["symbol"] == expected_symbol
    assert win["count"] == expected_count
    assert win["mult"] == expected_mult
    assert win["total"] == expected_mult  # total = mult w aktualnej implementacji


def test_wild_substitution_works():
    """
    Wild powinien zastąpić symbol w linii i dać maksymalną możliwą wygraną.
    """
    cfg = _cfg()
    board = [Symbol(cfg, s) for s in ["W", "A", "A", "A", "A"]]
    win = evaluate_single_line(board, cfg)

    assert win["symbol"] == "A"
    assert win["count"] == 5
    assert win["mult"] == 50
