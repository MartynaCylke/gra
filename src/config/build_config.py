from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json

from .helpers import convert_range_table, read_reels_csv, validate_symbols_on_reels


# --- Bazowe struktury ---

@dataclass
class Paytable:
    # Przechowujemy prosty przypadek (np. 3oak) w mapie "three_kind"
    # oraz ewentualnie pełną mapę (kind, symbol) -> value
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


@dataclass
class GameConfig:
    # Wspólne
    id: str
    mode: str = "balls"
    bet: int = 1
    basegame_type: str = "basegame"
    freegame_type: str = "freegame"

    # lines
    reels: Optional[List[List[str]]] = None           # 3 bębny -> [reel0, reel1, reel2]
    paytable: Optional[Paytable] = None
    special_symbols: Dict[str, List[str]] = None      # {"wild": ["W"], "scatter": ["S"], ...}
    freespin_triggers: Dict[str, Dict[int, int]] = None  # {"basegame": {3:10,...}, "freegame": {...}}
    reels_map: Dict[str, str] = None                  # np. {"BR0": "BR0.csv", "FR0": "FR0.csv"}
    reels_sets: Dict[str, List[List[str]]] = None     # wczytane paski per klucz (BR0, FR0)

    # balls
    colors: Optional[List[str]] = None
    weights: Optional[List[float]] = None
    balls_rules: Optional[BallsRules] = None

    # grid_balls
    rows: Optional[int] = None
    cols: Optional[int] = None
    grid_balls_rules: Optional[GridBallsRules] = None

    # betmodes
    betmodes: List[BetMode] = None


def _parse_betmodes(raw: dict, default_cost: float) -> List[BetMode]:
    out: List[BetMode] = []
    modes = raw.get("bet_modes", [])
    if not modes:
        out.append(BetMode(name="base", cost=float(default_cost), distributions=[Distribution("basegame", 1.0)]))
        return out
    for bm in modes:
        distributions = [Distribution(d["criteria"], float(d.get("quota", 0.0))) for d in bm.get("distributions", [])]
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


def _load_reels_for_game(game_id: str, raw: dict) -> Dict[str, List[List[str]]]:
    """
    Czyta reels z plików CSV wskazanych w raw["reels_files"] (mapa: key->filename),
    pliki muszą leżeć w games/<id>/reels/.
    Zwraca: {"BR0": [reel0, reel1, ...], "FR0": [...], ...}
    """
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


def load_config(game_id: str) -> GameConfig:
    cfg_path = Path("games") / game_id / "config.json"
    data = json.loads(cfg_path.read_text(encoding="utf-8"))
    mode = data.get("mode", "balls")
    bet = data.get("bet", 1)

    # Betmodes (wspólne)
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
    # Paytable: akceptujemy prosty "3oak" lub pełny "pay_group" (range)
    pt_three = None
    pt_full = None

    if "paytable" in data and "3oak" in data["paytable"]:
        pt_three = data["paytable"]["3oak"]

    if "pay_group" in data:
        # JSON kluczami nie mogą być tuple, więc w praktyce przyjmujemy listy: [[min,max], "SYM"]: value
        # tutaj konwertujemy do dict z krotkami
        normalized = {}
        for k, v in data["pay_group"].items():
            # k jest stringiem – jeśli użyjesz takiej formy, pomiń pay_group; dla uproszczenia nie parsujemy string-key
            pass  # optional: możesz rozszerzyć pod swój JSON
        # Jeśli chcesz używać pay_group – lepiej przygotuj w Pythonie, nie JSON.

    paytable = Paytable(three_kind=pt_three, full=pt_full)

    special_symbols = data.get("special_symbols", {}) or {}
    freespin_triggers = data.get("freespin_triggers", {}) or {}
    reels_sets = _load_reels_for_game(game_id, data)

    # Walidacja symboli na bębnach (jeśli mamy paski)
    if reels_sets:
        # wyciągamy listę symboli z paytable (jeśli three_kind – klucze to symbole)
        pay_syms = set()
        if paytable.three_kind:
            pay_syms.update(paytable.three_kind.keys())
        if paytable.full:
            pay_syms.update(sym for (_, sym) in paytable.full.keys())
        validate_symbols_on_reels(reels_sets, pay_syms, special_symbols)

    # Jeśli chcesz zdefiniować jeden aktywny zestaw (np. BR0) do szybkiej gry "lines",
    # możesz złożyć reels z jednego klucza (tu BR0) – inaczej użyjesz reels_sets per tryb w swoim runnerze
    active_lines_reels: Optional[List[List[str]]] = None
    if reels_sets:
        active_lines_reels = next(iter(reels_sets.values()))

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
    )
