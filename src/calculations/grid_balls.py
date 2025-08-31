from typing import List, Dict, Any
from src.config.build_config import GameConfig
from src.symbol import Symbol



def evaluate_grid_balls(board: List[List[Symbol]], cfg: GameConfig) -> Dict[str, Any]:
    """
    Sprawdzamy tylko dolny (ostatni) wiersz.
    Wygrana: wszystkie symbole w dolnym rzędzie takie same (Wildy traktujemy jak symbol, jeśli trzeba).
    """
    if not board:
        return {}

    last_row = board[-1]  # dolny wiersz
    if len(last_row) != (cfg.cols or 0):
        return {}

    # zamień na nazwy symboli dla łatwego sprawdzenia
    names = [s.name for s in last_row]

    if len(set(names)) == 1:
        mult = 0
        if cfg.grid_balls_rules:
            mult = int(getattr(cfg.grid_balls_rules, "bottom_row_all_same", 0))
        if mult > 0:
            return {
                "type": "bottom_row_all_same",
                "row_index": (cfg.rows - 1) if cfg.rows else 0,
                "color": names[0],
                "count": len(last_row),
                "mult": mult
            }

    return {}
