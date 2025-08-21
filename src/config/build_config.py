from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import json

from .helpers import convert_range_table, read_reels_csv, validate_symbols_on_reels

# --- Normalizacja warunków Distribution ---
def normalize_conditions(conditions: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Normalizuje nazwy pól w conditions, akceptując różne warianty pisowni:
      - force_wincap / forceWinCap / force_winCap
      - force_freegame / forceFreegame / force_freeGame
      - reel_weights / reels / reelWeights
      - mult_values / multiplier_values / multValues
      - scatter_triggers / scatterTriggers
    Zwraca słownik o kluczach: force_wincap, force_freegame, reel_weights, mult_values, scatter_triggers.
    """
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
    three_kind: Dict[str, int] = None
    full: Dict[Tuple[int, str], float] = None

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
    distributions: List[Distribution] = None

    # --- NOWA METODA ---
    def get_distribution_conditions(self) -> List[Dict[str, Any]]:
        """
        Zwraca listę znormalizowanych warunków Distribution dla tej instancji BetMode.
        """
        out = []
        if not self.distributions:
            return out
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
    special_symbols: Dict[str, List[str]] = None
    freespin_triggers: Dict[str, Dict[int, int]] = None
    reels_map: Dict[str, str] = None
    reels_sets: Dict[str, List[List[str]]] = None
    colors: Optional[List[str]] = None
    weights: Optional[List[float]] = None
    balls_rules: Optional[BallsRules] = None
    rows: Optional[int] = None
    cols: Optional[int] = None
    grid_balls_rules: Optional[GridBallsRules] = None
    betmodes: List[BetMode] = None
    paytable_4oak: Optional[Dict[str, int]] = None
    paytable_5oak: Optional[Dict[str, int]] = None

# --- Parsowanie BetModes i Distribution ---

def _parse_betmodes(raw: dict, default_cost: float) -> List[BetMode]:
    out: List[BetMode] = []
    modes = raw.get("bet_modes", [])
    if not modes:
        out.append(BetMode(name="base", cost=float(default_cost),
                           distributions=[Distribution("basegame", 1.0)]))
        return out

    def _dist(d: dict) -> Distribution:
        crit = str(d.get("criteria", "basegame"))
        q = float(d.get("quota", 0.0))
        wc = d.get("win_criteria")
        if wc is None:
            wc = d.get("winCap", d.get("wincap"))
        cond = normalize_conditions(d.get("conditions"))
        return Distribution(criteria=crit, quota=q, win_criteria=wc, conditions=cond)

    for bm in modes:
        distributions = [_dist(d) for d in bm.get("distributions", [])]
        out.append(
            BetMode(
                name=bm.get("name", "base"),
                cost=float(bm.get("cost", default_cost)),
                rtp=float(bm.get("rtp", 0.0)),
                max_win=float(bm.get("max_win", 0.0)),
                auto_close_disabled=bool(bm.get("auto_close_disabled", False)),
                is_feature=bool(bm.get("is_feature", False)),
                is_buybonus=bool(bm.get("is_buybonus", False)),
                distributions=distributions or [Distribution("basegame", 1.0)],
            )
        )
    return out

# --- Wczytywanie reels dla gry ---

def _load_reels_for_game(game_id: str, raw: dict) -> Dict[str, List[List[str]]]:
    reels_sets: Dict[str, List[List[str]]] = {}
    reels_files = raw.get("reels_files") or raw.get("reels")
    if not reels_files or not isinstance(reels_files, dict):
        return reels_sets
    base = Path("games") / game_id / "reels"
    for key, fname in reels_files.items():
        p = base / fname
        if not p.exists():
            raise FileNotFoundError(f"Reels CSV not found: {p}")
        reels_sets[key] = read_reels_csv(p)
    return reels_sets

# --- Wczytywanie całego configu gry ---

def load_config(game_id: str) -> GameConfig:
    cfg_path = Path("games") / game_id / "config.json"
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    mode = data.get("mode", "balls")
    bet = data.get("bet", 1)
    betmodes = _parse_betmodes(data, default_cost=bet)

    if mode == "grid_balls":
        return GameConfig(
            id=game_id,
            mode="grid_balls",
            bet=bet,
            colors=data["colors"],
            weights=data.get("weights"),
            rows=int(data["rows"]),
            cols=int(data["cols"]),
            grid_balls_rules=GridBallsRules(
                bottom_row_all_same=data.get("rules", {}).get("bottom_row_all_same", 0)
            ),
            betmodes=betmodes,
        )

    if mode == "balls":
        return GameConfig(
            id=game_id,
            mode="balls",
            bet=bet,
            colors=data["colors"],
            weights=data.get("weights"),
            balls_rules=BallsRules(
                three_same=data.get("rules", {}).get("three_same", 0),
                two_same=data.get("rules", {}).get("two_same", 0),
                all_different=data.get("rules", {}).get("all_different", 0),
            ),
            betmodes=betmodes,
        )

    # mode == "lines"
    pt_three = None
    pt_full = None
    if "paytable" in data and "3oak" in data["paytable"]:
        pt_three = data["paytable"]["3oak"]
    paytable = Paytable(three_kind=pt_three, full=pt_full)
    special_symbols = data.get("special_symbols", {}) or {}
    freespin_triggers = data.get("freespin_triggers", {}) or {}
    reels_sets = _load_reels_for_game(game_id, data)
    if reels_sets:
        pay_syms = set()
        if paytable.three_kind:
            pay_syms.update(paytable.three_kind.keys())
        if paytable.full:
            pay_syms.update(sym for (_, sym) in paytable.full.keys())
        validate_symbols_on_reels(reels_sets, pay_syms, special_symbols)
    active_lines_reels: Optional[List[List[str]]] = None
    if reels_sets:
        active_lines_reels = next(iter(reels_sets.values()))
    pt4 = data.get("paytable", {}).get("4oak")
    pt5 = data.get("paytable", {}).get("5oak")
    return GameConfig(
        id=game_id,
        mode="lines",
        bet=bet,
        reels=active_lines_reels,
        paytable=paytable,
        special_symbols=special_symbols,
        freespin_triggers=freespin_triggers,
        reels_map=data.get("reels_files") or data.get("reels"),
        reels_sets=reels_sets,
        betmodes=betmodes,
        paytable_4oak=pt4,
        paytable_5oak=pt5,
    )

