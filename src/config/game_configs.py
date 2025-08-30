from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ------------------------
# Definicje klas konfiguracji
# ------------------------

@dataclass
class BetMode:
    name: str
    description: Optional[str] = None

    def get_distribution_conditions(self) -> List[Dict[str, str]]:
        """Przykładowa metoda zwracająca warunki dla betmode."""
        return [{"condition": "default"}]


@dataclass
class GameConfig:
    id: str
    mode: str  # np. "lines", "grid_balls", "balls"
    bet: int
    basegame_type: str
    freegame_type: str
    reels: Optional[List[List[str]]] = None
    colors: Optional[List[str]] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    weights: Optional[List[int]] = None
    paytable: Optional[Dict[str, Dict[str, int]]] = None
    special_symbols: Optional[Dict[str, List[str]]] = None
    multiplier: Optional[int] = None
    betmodes: List[BetMode] = field(default_factory=list)


# ------------------------
# Przykładowe konfiguracje
# ------------------------

cfg_5reel = GameConfig(
    id="test_5reel",
    mode="lines",
    bet=1,
    basegame_type="basegame",
    freegame_type="freegame",
    reels=[
        ["A", "B", "C", "D", "E"],
        ["A", "B", "C", "D", "E"],
        ["A", "B", "C", "D", "E"],
        ["A", "B", "C", "D", "E"],
        ["A", "B", "C", "D", "E"]
    ],
    paytable={
        "three_kind": {"A": 10, "B": 5, "C": 3},
        "four_kind": {"A": 20, "B": 10, "C": 6},
        "five_kind": {"A": 50, "B": 25, "C": 15}
    },
    special_symbols={"wild": ["W"]},
    betmodes=[BetMode(name="5reel")]
)

cfg_3reel = GameConfig(
    id="test_3reel",
    mode="lines",
    bet=1,
    basegame_type="basegame",
    freegame_type="freegame",
    reels=[
        ["A", "B", "S"],
        ["A", "B", "S"],
        ["A", "B", "S"]
    ],
    paytable={
        "three_kind": {"A": 5, "B": 3, "S": 0}
    },
    special_symbols={"wild": ["W"], "scatter": ["S"]},
    betmodes=[BetMode(name="3reel")]
)
