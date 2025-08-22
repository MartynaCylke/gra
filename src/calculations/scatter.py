from typing import List, Dict, Any
from src.symbol.symbol import Symbol
from src.state.config import GameConfig

def evaluate_scatter(board: List[Symbol], cfg: GameConfig) -> Dict[str, Any]:
    """
    Ewaluator Scatterów: wygrane za ilość scatter symboli w całym boardzie.
    Zwraca {} jeśli brak wygranej.
    """
    if not cfg or not board:
        return {}

    scatter_symbol = cfg.special_symbols.get("scatter", "S")
    count = sum(1 for s in board if s.name == scatter_symbol)

    # Jeśli brak scatterów albo brak tabeli dla scattera -> brak wygranej
    if count < 3 or not cfg.paytable.scatter:
        return {}

    payout = cfg.paytable.scatter.get(count, 0)
    if payout <= 0:
        return {}

    return {
        "type": "scatter",
        "symbol": scatter_symbol,
        "count": count,
        "mult": payout
    }
