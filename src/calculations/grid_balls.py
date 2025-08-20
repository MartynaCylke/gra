from typing import List, Dict, Any
from src.config.build_config import GameConfig

def evaluate_grid_balls(board: List[List[str]], cfg: GameConfig) -> Dict[str, Any]:
    # Sprawdzamy tylko dolny (ostatni) wiersz
    if not board:
        return {}
    last_row = board[-1]  # wiersz nr 2 (0,1,2) przy rows=3
    if len(last_row) != (cfg.cols or 0):
        return {}

    # Warunek wygranej: wszystkie 5 kulek w dolnym rzędzie w tym samym kolorze
    if len(set(last_row)) == 1:
        mult = 0
        if cfg.grid_balls_rules:
            mult = int(getattr(cfg.grid_balls_rules, "bottom_row_all_same", 0))
        if mult > 0:
            return {
                "type": "bottom_row_all_same",
                "row_index": (cfg.rows - 1) if cfg.rows else 0,
                "color": last_row[0],
                "count": len(last_row),
                "mult": mult
            }
    return {}
