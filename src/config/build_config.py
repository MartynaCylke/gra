from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import json

@dataclass
class Paytable:
    three_kind: Dict[str, int]

@dataclass
class BallsRules:
    three_same: int = 0
    two_same: int = 0
    all_different: int = 0

@dataclass
class GridBallsRules:
    bottom_row_all_same: int = 0

@dataclass
class GameConfig:
    id: str
    mode: str = "balls"
    bet: int = 1

    # lines
    reels: Optional[List[List[str]]] = None
    paytable: Optional[Paytable] = None

    # balls (proste 3 kulki)
    colors: Optional[List[str]] = None
    weights: Optional[List[float]] = None
    balls_rules: Optional[BallsRules] = None

    # grid_balls (siatka 3x5)
    rows: Optional[int] = None
    cols: Optional[int] = None
    grid_balls_rules: Optional[GridBallsRules] = None

def load_config(game_id: str) -> GameConfig:
    cfg_path = Path("games") / game_id / "config.json"
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    mode = data.get("mode", "balls")

    if mode == "grid_balls":
        return GameConfig(
            id=game_id,
            mode="grid_balls",
            bet=data.get("bet", 1),
            colors=data["colors"],
            weights=data.get("weights"),
            rows=int(data["rows"]),
            cols=int(data["cols"]),
            grid_balls_rules=GridBallsRules(
                bottom_row_all_same=data.get("rules", {}).get("bottom_row_all_same", 0)
            ),
        )
    elif mode == "balls":
        return GameConfig(
            id=game_id,
            mode="balls",
            bet=data.get("bet", 1),
            colors=data["colors"],
            weights=data.get("weights"),
            balls_rules=BallsRules(
                three_same=data.get("rules", {}).get("three_same", 0),
                two_same=data.get("rules", {}).get("two_same", 0),
                all_different=data.get("rules", {}).get("all_different", 0),
            ),
        )
    else:
        # lines
        return GameConfig(
            id=game_id,
            mode="lines",
            bet=data.get("bet", 1),
            reels=data["reels"],
            paytable=Paytable(three_kind=data["paytable"]["3oak"]),
        )
