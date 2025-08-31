from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol import Symbol  # <- poprawione
from collections import Counter

def _wild_set(cfg: GameConfig) -> set:
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}

def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    best_symbol, best_value = None, 0
    pt = cfg.paytable
    if not pt:
        return "A"
    for symbol, value in (pt.five_kind or {}).items():
        if value > best_value:
            best_symbol, best_value = symbol, value
    if best_symbol:
        return best_symbol
    # fallback do 4- i 3-kind
    for symbol, value in (pt.four_kind or {}).items():
        if value > best_value:
            best_symbol, best_value = symbol, value
    for symbol, value in (pt.three_kind or {}).items():
        if value > best_value:
            best_symbol, best_value = symbol, value
    return best_symbol or "A"

def evaluate_single_line(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    if not board or not cfg.paytable:
        return {}

    wilds = _wild_set(cfg)
    names = [s.name for s in board]

    non_wilds = [n for n in names if n not in wilds]
    if not non_wilds:
        best = _best_symbol_for_all_wilds(cfg)
        count = len(names)
    else:
        counter = Counter(non_wilds)
        best, base_count = counter.most_common(1)[0]
        wild_count = sum(1 for n in names if n in wilds)
        count = base_count + wild_count

    mult = 0
    pt = cfg.paytable
    if count >= 5 and pt.five_kind:
        mult = pt.five_kind.get(best, 0)
    elif count == 4 and pt.four_kind:
        mult = pt.four_kind.get(best, 0)
    elif count == 3 and pt.three_kind:
        mult = pt.three_kind.get(best, 0)

    if mult > 0:
        return {
            "line": 0,
            "symbol": best,
            "count": count,
            "mult": mult,
            "total": mult
        }

    return {}
