from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol


def _wild_set(cfg: GameConfig) -> set:
    """
    Zwraca zbiór symboli Wild z configu (domyślnie {'W'})
    """
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    """
    Jeśli pierwsze 3 pozycje to same Wildy, wybierz symbol o najwyższej wypłacie z 3oak
    """
    if cfg.paytable and cfg.paytable.three_kind:
        return max(cfg.paytable.three_kind.items(), key=lambda kv: kv[1])[0]
    return "A"


def evaluate_single_line(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    """
    Minimalny evaluator 3‑bębnowy: ocenia TYLKO pierwsze 3 pozycje board (od lewej),
    z obsługą Wild (substytut). Zwraca {} gdy brak wygranej.
    """
    if not isinstance(board, list) or len(board) < 3 or not cfg.paytable or not cfg.paytable.three_kind:
        return {}

    wilds = _wild_set(cfg)

    s0, s1, s2 = board[0], board[1], board[2]

    # wybierz symbol do rozliczenia: pierwszy nie-Wild z lewej; gdy same Wildy → najlepszy z 3oak
    target_symbol = next((s for s in (s0, s1, s2) if s.name not in wilds), None)
    target_name = target_symbol.name if target_symbol else _best_symbol_for_all_wilds(cfg)

    def matches(a: Symbol, b_name: str) -> bool:
        return (a.name == b_name) or (a.name in wilds) or (b_name in wilds)

    if matches(s0, target_name) and matches(s1, target_name) and matches(s2, target_name):
        mult = int(cfg.paytable.three_kind.get(target_name, 0))
        if mult > 0:
            return {"line": 0, "symbol": target_name, "count": 3, "mult": mult}

    return {}
