from dataclasses import dataclass
from typing import Dict, Any
from src.config.build_config import GameConfig

@dataclass
class Wallet:
    cfg: GameConfig
    balance: int = 0

    def settle(self, win: Dict[str, Any]) -> int:
        bet = self.cfg.bet
        payout = 0
        if win:
            payout = int(win.get("mult", 0)) * bet
        self.balance += -bet + payout
        return payout
