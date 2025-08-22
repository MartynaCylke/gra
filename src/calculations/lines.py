from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol


def _wild_set(cfg: GameConfig) -> set:
    """Zwraca zbiór symboli Wild z configu (domyślnie {'W'})"""
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    """Jeśli wszystkie symbole to Wildy, wybierz symbol o najwyższej wypłacie z paytable"""
    if cfg.paytable and cfg.paytable.three_kind:
        return max(cfg.paytable.three_kind.items(), key=lambda kv: kv[1])[0]
    return "A"


def evaluate_single_line(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    """
    Evaluator liniowy: obsługuje dowolną długość boardu (3,4,5),
    z uwzględnieniem Wild jako substytutów.
    Zwraca {} gdy brak wygranej.
    """
    if not isinstance(board, list) or len(board) < 3 or not cfg.paytable or not cfg.paytable.three_kind:
        return {}

    wilds = _wild_set(cfg)
    # pierwszy symbol nie-Wild lub najlepszy, jeśli same Wildy
    target_symbol = next((s for s in board if s.name not in wilds), None)
    target_name = target_symbol.name if target_symbol else _best_symbol_for_all_wilds(cfg)

    def matches(sym: Symbol, name: str) -> bool:
        return sym.name == name or sym.name in wilds or name in wilds

    # liczymy ile kolejnych symboli pasuje do target_name
    count = 0
    for sym in board:
        if matches(sym, target_name):
            count += 1
        else:
            break  # linia kończy się przy pierwszym niepasującym

    # sprawdzamy paytable wg liczby symboli w linii
    mult = cfg.paytable.three_kind.get(target_name) if count >= 3 else 0
    # jeśli masz paytable dla 4 i 5, można rozbudować tutaj dynamicznie

    if mult > 0 and count >= 3:
        return {"line": 0, "symbol": target_name, "count": count, "mult": mult}

    return {}
