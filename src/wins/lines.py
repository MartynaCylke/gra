from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol import Symbol



def _wild_set(cfg: GameConfig) -> set:
    """Zwraca zbiór symboli Wild z configu (domyślnie {'W'})"""
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    """Jeśli wszystkie symbole to Wildy, wybierz symbol o najwyższej wypłacie z paytable"""
    paytable_symbols = {}
    if cfg.paytable:
        for key in ["three_kind", "four_kind", "five_kind"]:
            kind_table = getattr(cfg.paytable, key, None)
            if kind_table:
                for sym, val in kind_table.items():
                    paytable_symbols[sym] = max(paytable_symbols.get(sym, 0), val)
    if paytable_symbols:
        return max(paytable_symbols.items(), key=lambda kv: kv[1])[0]
    return "A"


def evaluate_single_line(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    """
    Evaluator liniowy: obsługuje dowolną długość boardu (3,4,5,...),
    z uwzględnieniem Wild jako substytutów.
    Zwraca {} gdy brak wygranej.
    """
    if not isinstance(board, list) or len(board) < 3 or not cfg.paytable:
        return {}

    wilds = _wild_set(cfg)

    # znajdź pierwszy nie-Wild symbol lub najlepszy jeśli wszystkie Wild
    target_symbol = next((s for s in board if s.name not in wilds), None)
    target_name = target_symbol.name if target_symbol else _best_symbol_for_all_wilds(cfg)

    def matches(sym: Symbol, name: str) -> bool:
        """Sprawdza czy symbol pasuje do target_name (uwzględnia Wild)"""
        return sym.name == name or sym.name in wilds or name in wilds

    # licz kolejne pasujące symbole od początku boardu
    count = 0
    for sym in board:
        if matches(sym, target_name):
            count += 1
        else:
            break

    # wybierz najwyższą dostępną wartość z paytable
    mult = 0
    if count >= 3 and cfg.paytable:
        # dynamicznie sprawdzamy, od największej liczby symboli do najmniejszej
        for n, table_name in sorted([(5, "five_kind"), (4, "four_kind"), (3, "three_kind")], reverse=True):
            if count >= n:
                kind_table = getattr(cfg.paytable, table_name, None)
                if kind_table:
                    mult = kind_table.get(target_name, 0)
                    if mult > 0:
                        break

    if mult > 0:
        return {"line": 0, "symbol": target_name, "count": count, "mult": mult}

    return {}
