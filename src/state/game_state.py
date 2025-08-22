from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Optional
from src.config.build_config import GameConfig, BetMode
from src.utils.rng import Rng
from src.events.events import create_spin_event, update_freespin_event, create_win_event
from src.symbol.symbol import Symbol

BoardType = Union[List[str], List[List[str]]]


@dataclass
class GameState:
    cfg: GameConfig
    sim: int = 0  # indeks spinu (0..N-1)
    trace: bool = False  # gdy True, Book zawiera szczegółowe events
    book: Dict[str, Any] = field(default_factory=dict)
    library: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=lambda: {"spins": 0, "wins": 0, "payoutMultSum": 0})
    last_board: Optional[BoardType] = None
    free_spins: int = 0

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
        self.book = {
            "id": self.sim + 1,
            "payoutMultiplier": 0,
            "events": [] if self.trace else [],
            "criteria": criteria or self.cfg.mode,
            "baseGameWins": 0,
            "freeGameWins": 0,
        }

    def add_event(self, ev: Dict[str, Any]) -> None:
        if self.trace and isinstance(self.book.get("events"), list):
            self.book["events"].append(ev)

    def finalize_book(self, payout_mult: int) -> Dict[str, Any]:
        self.book["payoutMultiplier"] = int(payout_mult)
        self.totals["spins"] += 1
        if payout_mult > 0:
            self.totals["wins"] += 1
        self.totals["payoutMultSum"] += int(payout_mult)
        self.library.append(dict(self.book))
        return self.book

    def run_spin(self, rng: Rng, evaluator) -> Dict[str, Any]:
        """
        Wykonuje pojedynczy spin, generuje board, ocenia wygrane i dodaje eventy.
        """
        self.reset_book(criteria=self.cfg.mode)

        # --- wygeneruj board ---
        raw_board = self.make_board(rng)
        # Zamień każdy symbol na obiekt Symbol
        if isinstance(raw_board[0], list):  # grid_balls
            board = [[Symbol(self.cfg, s) for s in row] for row in raw_board]
        else:
            board = [Symbol(self.cfg, s) for s in raw_board]

        self.last_board = board  # potrzebne do eventów

        # --- event rozpoczęcia spinu ---
        create_spin_event(self)

        # --- oblicz wygraną ---
        win = evaluator(board, self.cfg)
        payout_mult = int(win.get("mult", 0)) if win else 0

        # --- event wygranej (jeśli jest) ---
        if win:
            create_win_event(self, symbol=win.get("symbol"), count=win.get("count"), mult=win.get("mult"))

        # --- event freespinu (jeśli dotyczy) ---
        if self.free_spins > 0:
            update_freespin_event(self)

        # --- dodaj board i wygraną do book jako spin_result event ---
        self.add_event({"type": "spin_result", "board": board, "win": win or {}})

        return self.finalize_book(payout_mult)

    def snapshot(self) -> Dict[str, Any]:
        """
        Zwraca stan gry do front-endu (bez spinów).
        """
        return {
            "last_board": self.last_board,
            "free_spins": self.free_spins,
            "totals": self.totals.copy(),
            "current_book": self.book.copy(),
        }

    # ------------ Nowa funkcja ------------
    def get_distribution_conditions(self, betmode_name: str) -> List[Dict[str, Any]]:
        """
        Zwraca listę znormalizowanych warunków dystrybucji dla podanego betmode.
        """
        bm: Optional[BetMode] = next(
            (b for b in self.cfg.betmodes if b.name == betmode_name), None
        )
        if not bm:
            raise ValueError(f"BetMode o nazwie '{betmode_name}' nie istnieje w konfiguracji.")

        # Korzystamy z metody BetMode.get_distribution_conditions, aby mieć zawsze znormalizowane warunki
        return bm.get_distribution_conditions()
