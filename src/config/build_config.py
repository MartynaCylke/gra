from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import json

# --- Normalizacja warunków Distribution ---
def normalize_conditions(conditions: Dict[str, Any] | None) -> Dict[str, Any]:
    out = {
        "force_wincap": False,
        "force_freegame": False,
        "reel_weights": None,
        "mult_values": None,
        "scatter_triggers": None,
    }
    if not conditions:
        return out

    def get_any(keys: Tuple[str, ...], default=None):
        for k in keys:
            if k in conditions:
                return conditions[k]
        lower = {str(k).lower(): v for k, v in conditions.items()}
        for k in keys:
            if k.lower() in lower:
                return lower[k.lower()]
        return default

    out["force_wincap"] = bool(get_any(("force_wincap", "forceWinCap", "force_winCap"), False))
    out["force_freegame"] = bool(get_any(("force_freegame", "forceFreegame", "force_freeGame"), False))
    out["reel_weights"] = get_any(("reel_weights", "reels", "reelWeights"))
    out["mult_values"] = get_any(("mult_values", "multiplier_values", "multValues"))
    out["scatter_triggers"] = get_any(("scatter_triggers", "scatterTriggers"))
    return out

# --- Bazowe struktury ---
@dataclass
class Paytable:
    three_kind: Dict[str, int] = field(default_factory=dict)
    four_kind: Optional[Dict[str, int]] = field(default_factory=dict)
    five_kind: Optional[Dict[str, int]] = field(default_factory=dict)
    full: Dict[Tuple[int, str], float] = field(default_factory=dict)

@dataclass
class BallsRules:
    three_same: int = 0
    two_same: int = 0
    all_different: int = 0

@dataclass
class GridBallsRules:
    bottom_row_all_same: int = 0

@dataclass
class Distribution:
    criteria: str
    quota: float
    win_criteria: Optional[float] = None
    conditions: Optional[Dict[str, Any]] = None

@dataclass
class BetMode:
    name: str
    cost: float
    rtp: float = 0.0
    max_win: float = 0.0
    auto_close_disabled: bool = False
    is_feature: bool = False
    is_buybonus: bool = False
    distributions: List[Distribution] = field(default_factory=list)

    def get_distribution_conditions(self) -> List[Dict[str, Any]]:
        out = []
        for dist in self.distributions:
            cond = normalize_conditions(dist.conditions)
            out.append(cond)
        return out

@dataclass
class GameConfig:
    id: str
    mode: str = "balls"
    bet: int = 1
    basegame_type: str = "basegame"
    freegame_type: str = "freegame"
    reels: Optional[List[List[str]]] = None
    paytable: Optional[Paytable] = None
    special_symbols: Dict[str, List[str]] = field(default_factory=dict)
    freespin_triggers: Dict[str, Dict[int, int]] = field(default_factory=dict)
    reels_map: Dict[str, str] = field(default_factory=dict)
    reels_sets: Dict[str, List[List[str]]] = field(default_factory=dict)
    colors: Optional[List[str]] = None
    weights: Optional[List[float]] = None
    balls_rules: Optional[BallsRules] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    grid_balls_rules: Optional[GridBallsRules] = None
    betmodes: List[BetMode] = field(default_factory=list)
    paytable_4oak: Optional[Dict[str, int]] = None
    paytable_5oak: Optional[Dict[str, int]] = None
    multiplier: Optional[int] = None
    bonus: Optional[str] = None

# --- build_test_config ---
def build_test_config(
    reels: Optional[List[List[str]]] = None,
    scatter: Optional[str] = None,
    multiplier: Optional[int] = None,
    bonus: Optional[str] = None,
) -> GameConfig:
    paytable = Paytable(
        three_kind={"A": 10, "B": 5, "C": 2},
        four_kind={"A": 20, "B": 10, "C": 4},
        five_kind={"A": 50, "B": 25, "C": 10},
    )
    cfg = GameConfig(
        id="test",
        mode="lines",
        colors=["A", "B", "C", "S", "W"],
        reels=reels or [["A", "B", "C", "W", "S"]] * 5,
        betmodes=[BetMode(name="test", cost=1.0)],
        paytable=paytable,
        rows=1,
        cols=5,
        special_symbols={"wild": ["W"], "scatter": [scatter]} if scatter else {"wild": ["W"]},
        multiplier=multiplier,
        bonus=bonus,
    )
    return cfg

# --- load_config ---
def load_config(game_id: str, base_path: Optional[Path] = None) -> GameConfig:
    base_path = base_path or Path(__file__).parent
    config_path = base_path / f"{game_id}.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku konfiguracyjnego: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    paytable = None
    if "paytable" in data:
        pt = data["paytable"]
        paytable = Paytable(
            three_kind=pt.get("three_kind", {}),
            four_kind=pt.get("four_kind", {}),
            five_kind=pt.get("five_kind", {}),
            full=pt.get("full", {}),
        )

    betmodes = []
    for bm in data.get("betmodes", []):
        distributions = [
            Distribution(
                criteria=d.get("criteria"),
                quota=d.get("quota"),
                win_criteria=d.get("win_criteria"),
                conditions=d.get("conditions"),
            )
            for d in bm.get("distributions", [])
        ]
        betmodes.append(
            BetMode(
                name=bm["name"],
                cost=bm["cost"],
                rtp=bm.get("rtp", 0.0),
                max_win=bm.get("max_win", 0.0),
                auto_close_disabled=bm.get("auto_close_disabled", False),
                is_feature=bm.get("is_feature", False),
                is_buybonus=bm.get("is_buybonus", False),
                distributions=distributions,
            )
        )

    cfg = GameConfig(
        id=data["id"],
        mode=data.get("mode", "balls"),
        bet=data.get("bet", 1),
        basegame_type=data.get("basegame_type", "basegame"),
        freegame_type=data.get("freegame_type", "freegame"),
        reels=data.get("reels"),
        paytable=paytable,
        special_symbols=data.get("special_symbols", {}),
        freespin_triggers=data.get("freespin_triggers", {}),
        reels_map=data.get("reels_map", {}),
        reels_sets=data.get("reels_sets", {}),
        colors=data.get("colors"),
        weights=data.get("weights"),
        balls_rules=BallsRules(**data["balls_rules"]) if data.get("balls_rules") else None,
        rows=data.get("rows"),
        cols=data.get("cols"),
        grid_balls_rules=GridBallsRules(**data["grid_balls_rules"]) if data.get("grid_balls_rules") else None,
        betmodes=betmodes,
        paytable_4oak=data.get("paytable_4oak"),
        paytable_5oak=data.get("paytable_5oak"),
        multiplier=data.get("multiplier"),
        bonus=data.get("bonus"),
    )
    return cfg
