from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Optional
from src.config.build_config import GameConfig
from src.utils.rng import Rng

BoardType = Union[List[str], List[List[str]]]

@dataclass
class GameState:
    cfg: GameConfig
    sim: int = 0  # indeks spinu (0..N-1)
    trace: bool = False  # gdy True, Book zawiera szczegółowe events
    book: Dict[str, Any] = field(default_factory=dict)
    library: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=lambda: {"spins": 0, "wins": 0, "payoutMultSum": 0})

    def make_board(self, rng: Rng) -> BoardType:
        if self.cfg.mode == "grid_balls":
            assert self.cfg.colors and self.cfg.rows and self.cfg.cols
            return [
                [rng.choice_weighted(self.cfg.colors, self.cfg.weights) for _ in range(self.cfg.cols)]
                for _ in range(self.cfg.rows)
            ]
        elif self.cfg.mode == "balls":
            assert self.cfg.colors
            return [rng.choice_weighted(self.cfg.colors, self.cfg.weights) for _ in range(3)]
        else:
            assert self.cfg.reels, "Brak 'reels' w configu gry lines"
            return [rng.choice(reel) for reel in self.cfg.reels]

    # ------------ State Machine hooks ------------
    def reset_book(self, criteria: Optional[str] = None) -> None:
        # “Book” = wynik jednej rundy (spinu)
        self.book = {
            "id": self.sim + 1,             # 1..N
            "payoutMultiplier": 0,          # int (x bet)
            "events": [] if self.trace else [],
            "criteria": criteria or self.cfg.mode,
            "baseGameWins": 0,              # proste pola do zgodności z opisem
            "freeGameWins": 0,
        }

    def add_event(self, ev: Dict[str, Any]) -> None:
        if self.trace and isinstance(self.book.get("events"), list):
            self.book["events"].append(ev)

    def finalize_book(self, payout_mult: int) -> Dict[str, Any]:
        self.book["payoutMultiplier"] = int(payout_mult)
        # prosta kumulacja (cumulative win manager)
        self.totals["spins"] += 1
        if payout_mult > 0:
            self.totals["wins"] += 1
        self.totals["payoutMultSum"] += int(payout_mult)
        # do biblioteki
        self.library.append(dict(self.book))
        return self.book

    def run_spin(self, rng: Rng, evaluator) -> Dict[str, Any]:
        self.reset_book(criteria=self.cfg.mode)
        board = self.make_board(rng)
        win = evaluator(board, self.cfg)
        payout_mult = int(win.get("mult", 0)) if win else 0
        # opcjonalnie zapis eventu do Book (trace)
        self.add_event({"board": board, "win": win or {}})
        return self.finalize_book(payout_mult)

    def snapshot(self):
        return {}

