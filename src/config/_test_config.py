from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Paytable:
    three_kind: Dict[str, int]
    four_kind: Optional[Dict[str, int]] = None
    five_kind: Optional[Dict[str, int]] = None


@dataclass
class TestConfig:
    id: str = "test"
    mode: str = "lines"
    bet: int = 1
    basegame_type: str = "basegame"
    freegame_type: str = "freegame"
    reels: List[List[str]] = None
    paytable: Paytable = None
    special_symbols: Dict[str, List[str]] = None


def build_test_config(
    scatter: str = "S",
    multiplier: int = 2,
    bonus: str = "bonus",
) -> TestConfig:
    """
    Tworzy testowy config gry.
    """
    return TestConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[["A", "B", "C", "W", scatter]],
        paytable=Paytable(
            three_kind={"A": 10, "B": 5, "C": 2},
            four_kind={"A": 20, "B": 10, "C": 4},
            five_kind={"A": 50, "B": 25, "C": 10},
        ),
        special_symbols={
            "wild": ["W"],
            "scatter": [scatter],
            "bonus": [bonus],
            "multiplier": [str(multiplier)],
        },
    )
