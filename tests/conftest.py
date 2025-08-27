import sys
from pathlib import Path
import pytest
from src.config.build_config import GameConfig, Paytable

# dodaj katalog główny (gra/) do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def cfg_5reel():
    """
    Konfiguracja 5-bębnowa do testów liniowych i wild
    """
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
        ],
        paytable=Paytable(
            three_kind={"A": 10, "B": 5, "C": 3},
            four_kind={"A": 20, "B": 10, "C": 6},
            five_kind={"A": 50, "B": 25, "C": 15}
        ),
        special_symbols={"wild": ["W"]},
    )


@pytest.fixture
def cfg_3reel():
    """
    Konfiguracja 3-bębnowa do testów scatter i bonusów
    """
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "S"],
            ["A", "B", "S"],
            ["A", "B", "S"]
        ],
        paytable=Paytable(
            three_kind={"A": 5, "B": 3, "S": 0}
        ),
        special_symbols={"wild": ["W"], "scatter": ["S"]},
    )
