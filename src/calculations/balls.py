from typing import List, Dict, Any
from src.config.build_config import GameConfig, BallsRules

def evaluate_balls(board: List[str], cfg: GameConfig) -> Dict[str, Any]:
    # Zasady: 3 te same, 3 różne, 2 te same
    rules: BallsRules = cfg.balls_rules or BallsRules()
    s = set(board)

    if len(s) == 1:
        mult = rules.three_same
        return {"type": "three_same", "count": 3, "mult": mult} if mult > 0 else {}
    elif len(s) == 3:
        mult = rules.all_different
        return {"type": "all_different", "count": 3, "mult": mult} if mult > 0 else {}
    else:
        # len(s) == 2 -> dokładnie 2 takie same
        mult = rules.two_same
        return {"type": "two_same", "count": 2, "mult": mult} if mult > 0 else {}
