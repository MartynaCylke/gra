from typing import List, Dict, Any
from src.config.build_config import GameConfig

def evaluate_single_line(board: List[str], cfg: GameConfig) -> Dict[str, Any]:
    s0, s1, s2 = board
    wild = 'W'

    def matches(a, b):
        return (a == b) or (a == wild) or (b == wild)

    candidates = {s for s in [s0, s1, s2] if s != wild}
    symbol = next(iter(candidates), 'A')

    if matches(s0, symbol) and matches(s1, symbol) and matches(s2, symbol):
        payout_mult = (cfg.paytable.three_kind.get(symbol, 0) if cfg.paytable else 0)
        if payout_mult > 0:
            return {"line": 0, "symbol": symbol, "count": 3, "mult": payout_mult}
    return {}
