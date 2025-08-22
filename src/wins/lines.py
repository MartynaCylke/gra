from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol


def _wild_set(cfg: GameConfig) -> set:
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    if cfg.paytable and cfg.paytable.three_kind:
        return max(cfg.paytable.three_kind.items(), key=lambda kv: kv[1])[0]
    return "A"


def evaluate_single_line(board: List[Symbol], cfg: GameConfig, line_index: int = 0) -> Dict[str, Any]:
    if not board or not cfg.paytable or not cfg.paytable.three_kind:
        return {}

    wilds = _wild_set(cfg)

    # target symbol: pierwszy nie-wild lub najlepszy symbol z paytable
    target_symbol = next((s for s in board if s.name not in wilds), None)
    target_name = target_symbol.name if target_symbol else _best_symbol_for_all_wilds(cfg)

    # liczymy ile symboli od lewej pasuje do target_name
    count = 0
    for s in board:
        if s.name == target_name or s.name in wilds:
            count += 1
        else:
            break

    # dopasowanie do paytable
    mult = cfg.paytable.three_kind.get(target_name, 0) if count >= 3 else 0

    if mult > 0:
        return {"line": line_index, "symbol": target_name, "count": count, "mult": mult}

    return {}
