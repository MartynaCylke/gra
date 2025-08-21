from dataclasses import dataclass
from typing import Dict, Any
from src.config.build_config import GameConfig

@dataclass
class Wallet:
    cfg: GameConfig
    balance: int = 0

    def settle(self, win_data: Dict[str, Any]) -> int:
        """
        Aktualizuje balans na podstawie całego win_data.
        win_data powinno mieć strukturę:
        {
            "totalWin": float,
            "wins": [ ... ]
        }
        """
        bet = self.cfg.bet
        payout = int(win_data.get("totalWin", 0))
        self.balance += -bet + payout
        return payout
