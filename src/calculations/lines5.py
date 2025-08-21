from typing import List, Dict, Any, Optional
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol


def _wild_set(cfg: GameConfig) -> set:
    """
    Zwraca zbiór symboli Wild z configu (domyślnie {'W'}).
    """
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    """
    Jeśli cała linia to Wildy, wybierz symbol o najwyższej wypłacie (na podstawie 3oak).
    """
    if cfg.paytable and cfg.paytable.three_kind:
        return max(cfg.paytable.three_kind.items(), key=lambda kv: kv[1])[0]
    return "A"


def _read_extra_paytable(cfg: GameConfig, key: str) -> Optional[Dict[str, int]]:
    try:
        return getattr(cfg, key)
    except Exception:
        return None


def evaluate_lines_5reel(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    """
    Evaluator dla pojedynczej linii 5-bębnowej (od lewej, Wild zastępuje).
    Zwraca dict np. {"line": 0, "symbol": "A", "count": 4, "mult": 10} lub {} gdy brak wygranej.
    """
    if not isinstance(board, list) or len(board) < 5:
        return {}

    wilds = _wild_set(cfg)

    # Wyznacz symbol celu: pierwszy nie-wild z lewej
    target = None
    for s in board:
        if s.name not in wilds:
            target = s.name
            break
    if target is None:
        target = _best_symbol_for_all_wilds(cfg)

    # Policz ile kolejnych symboli od lewej pasuje (target lub Wild)
    n = 0
    for s in board:
        if s.name == target or s.name in wilds:
            n += 1
        else:
            break

    if n < 3 or not cfg.paytable:
        return {}

    three_map = cfg.paytable.three_kind or {}
    four_map = _read_extra_paytable(cfg, "paytable_4oak")
    five_map = _read_extra_paytable(cfg, "paytable_5oak")

    mult = 0
    if n >= 5:
        if five_map and target in five_map:
            mult = int(five_map[target])
        else:
            base = int(three_map.get(target, 0))
            mult = 4 * base
    elif n == 4:
        if four_map and target in four_map:
            mult = int(four_map[target])
        else:
            base = int(three_map.get(target, 0))
            mult = 2 * base
    else:
        mult = int(three_map.get(target, 0))

    if mult <= 0:
        return {}

    return {"line": 0, "symbol": target, "count": n, "mult": mult}
