from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Optional
from src.config.build_config import GameConfig, BetMode
from src.utils.rng import Rng
from src.events.events import (
    create_spin_event,
    update_freespin_event,
    create_win_event,
    create_bonus_event,
    create_multiplier_event
)
from src.symbol.symbol import Symbol
import json

BoardType = Union[List[str], List[List[str]]]

@dataclass
class GameState:
    cfg: GameConfig
    sim: int = 0
    trace: bool = False
    book: Dict[str, Any] = field(default_factory=dict)
    library: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=lambda: {"spins": 0, "wins": 0, "payoutMultSum": 0})
    last_board: Optional[BoardType] = None
    free_spins: int = 0
    temp_wins: List[Dict[str, Any]] = field(default_factory=list)  # dla custom defined events

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
        else:  # lines
            assert self.cfg.reels, "Brak 'reels' w configu gry lines"
            return [rng.choice(reel) for reel in self.cfg.reels]

    def reset_book(self, criteria: Optional[str] = None) -> None:
        self.book = {
            "id": self.sim + 1,
            "payoutMultiplier": 0,
            "events": [] if self.trace else [],
            "criteria": criteria or self.cfg.mode,
            "baseGameWins": 0,
            "freeGameWins": 0,
            "scatterWins": 0,
        }

    def add_event(self, ev: Dict[str, Any]) -> None:
        if self.trace and isinstance(self.book.get("events"), list):
            ev["index"] = len(self.book["events"])
            self.book["events"].append(ev)

    def record(self, description: dict) -> None:
        """Zapisuje niestandardowe zdarzenie w temp_wins."""
        if not isinstance(description, dict):
            raise ValueError("description musi być słownikiem")
        entry = dict(description)
        entry["book_id"] = self.book.get("id")
        self.temp_wins.append(entry)

    def imprint_wins(self, filepath: str) -> None:
        """Finalizuje temp_wins i zapisuje je do force_record_<betmode>.json"""
        force_records = {}
        for entry in self.temp_wins:
            key = tuple(sorted(entry.items()))
            if key not in force_records:
                force_records[key] = {"search": dict(entry), "timesTriggered": 0, "bookIds": []}
            force_records[key]["timesTriggered"] += 1
            if entry["book_id"] not in force_records[key]["bookIds"]:
                force_records[key]["bookIds"].append(entry["book_id"])
        with open(filepath, "w") as f:
            json.dump(list(force_records.values()), f, indent=4)

    def finalize_book(self, payout_mult: int) -> Dict[str, Any]:
        self.book["payoutMultiplier"] = int(payout_mult)
        self.totals["spins"] += 1
        if payout_mult > 0:
            self.totals["wins"] += 1
        self.totals["payoutMultSum"] += int(payout_mult)
        self.library.append(dict(self.book))
        return self.book

    def run_spin(self, rng: Rng, evaluator) -> Dict[str, Any]:
        self.reset_book(criteria=self.cfg.mode)
        raw_board = self.make_board(rng)

        # Tworzymy Symbol obiekty
        if isinstance(raw_board[0], list):
            board = [[Symbol(self.cfg, s) for s in row] for row in raw_board]
            flat_board = [s for row in board for s in row]
        else:
            board = [Symbol(self.cfg, s) for s in raw_board]
            flat_board = board
        self.last_board = board

        # Spin start
        create_spin_event(self)

        # Wygrana liniowa
        win = evaluator(board, self.cfg)
        payout_mult = int(win.get("mult", 0)) if win else 0
        if win:
            create_win_event(self, symbol=win.get("symbol"), count=win.get("count"), mult=win.get("mult"))

        # Scatter i free spins
        scatter_symbol = getattr(self.cfg, "scatter", None)
        if not scatter_symbol and self.cfg.special_symbols:
            scatter_symbol = self.cfg.special_symbols.get("scatter", [None])[0]

        scatter_count = sum(1 for s in flat_board if s.name == scatter_symbol) if scatter_symbol else 0
        scatter_wins = 0
        if scatter_count >= 3:
            self.free_spins += 10
            scatter_wins = scatter_count
            self.add_event({"type": "scatter_event", "symbol": scatter_symbol, "count": scatter_count, "wins": scatter_wins})
            create_bonus_event(self, bonus_type="freespin_bonus", value=10)
            # zapis niestandardowego eventu
            self.record({
                "kind": scatter_count,
                "symbol": scatter_symbol,
                "gametype": getattr(self, "gametype", self.cfg.mode)  # fallback
            })

        self.book["scatterWins"] = scatter_wins

        # Aktualizacja free spins
        if self.free_spins > 0:
            update_freespin_event(self)

        # Multiplier
        if getattr(self.cfg, "multiplier", None):
            create_multiplier_event(self, self.cfg.multiplier)

        # Spin result
        self.add_event({
            "type": "spin_result",
            "board": [s.name for s in flat_board],
            "win": win or {},
            "scatterWins": scatter_wins,
        })

        return self.finalize_book(payout_mult)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "last_board": self.last_board,
            "free_spins": self.free_spins,
            "totals": self.totals.copy(),
            "current_book": self.book.copy(),
        }

    def get_distribution_conditions(self, betmode_name: str) -> List[Dict[str, Any]]:
        bm: Optional[BetMode] = next((b for b in self.cfg.betmodes if b.name == betmode_name), None)
        if not bm:
            raise ValueError(f"BetMode o nazwie '{betmode_name}' nie istnieje w konfiguracji.")
        return bm.get_distribution_conditions()
