from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Paytable:
    three_kind: Dict[str, int] = field(default_factory=dict)
    four_kind: Optional[Dict[str, int]] = field(default_factory=dict)
    five_kind: Optional[Dict[str, int]] = field(default_factory=dict)
    full: Optional[Dict[tuple, int]] = field(default_factory=dict)

@dataclass
class TestConfig:
    id: str = "test"
    mode: str = "lines"
    bet: int = 1
    basegame_type: str = "basegame"
    freegame_type: str = "freegame"
    reels: List[List[str]] = field(default_factory=list)
    paytable: Paytable = field(default_factory=Paytable)
    special_symbols: Dict[str, List[str]] = field(default_factory=dict)

def build_test_config(
    scatter: str = "S",
    multiplier: int = 2,
    bonus: str = "bonus",
) -> TestConfig:
    """
    Tworzy testowy config gry dla evaluatorów i GameState.
    """
    return TestConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[["A", "B", "C", "W", scatter]] * 5,
        paytable=Paytable(
            three_kind={"A": 10, "B": 5, "C": 2},
            four_kind={"A": 20, "B": 10, "C": 4},
            five_kind={"A": 50, "B": 25, "C": 10},
            full={
                (3, "A"): 10, (3, "B"): 5, (3, "C"): 2,
                (4, "A"): 20, (4, "B"): 10, (4, "C"): 4,
                (5, "A"): 50, (5, "B"): 25, (5, "C"): 10
            }
        ),
        special_symbols={
            "wild": ["W"],
            "scatter": [scatter],
            "bonus": [bonus],
            "multiplier": [str(multiplier)],
        },
    )
