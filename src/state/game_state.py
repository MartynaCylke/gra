from dataclasses import dataclass, field
from typing import List, Union, Dict, Any, Optional
from src.config.build_config import GameConfig, BetMode
from src.symbol.symbol import Symbol
from src.board.board import Board
from src.utils.rng import Rng
from src.utils.force_loader import ForceLoader
from src.events.events import (
    create_spin_event,
    update_freespin_event,
    create_win_event,
    create_bonus_event,
    create_multiplier_event
)
import json

BoardType = Union[List[str], List[List[str]]]

@dataclass
class GameState:
    cfg: GameConfig
    sim: int = 0
    trace: bool = True
    book: Dict[str, Any] = field(default_factory=dict)
    library: List[Dict[str, Any]] = field(default_factory=list)
    totals: Dict[str, Any] = field(default_factory=lambda: {"spins": 0, "wins": 0, "payoutMultSum": 0})
    last_board: Optional[BoardType] = None
    free_spins: int = 0
    temp_wins: List[Dict[str, Any]] = field(default_factory=list)
    force_loader: ForceLoader = field(default_factory=ForceLoader, init=False)
    force_enabled: bool = True

    # --- Board-related fields ---
    board: Optional[Board] = None
    board_data: list = field(default_factory=list)
    special_symbols_on_board: dict = field(default_factory=dict)
    reel_positions: list = field(default_factory=list)
    reelstrip_id: str = ""
    top_padding: list = field(default_factory=list)
    bottom_padding: list = field(default_factory=list)
    anticipation: list = field(default_factory=list)
    betmode: Optional[BetMode] = None

    def initialize_betmode(self):
        if not self.betmode:
            self.betmode = self.cfg.betmodes[0] if self.cfg.betmodes else None

    # --- Board creation ---
    def make_board_from_reelstrips(self):
        self.initialize_betmode()
        self.board = Board(cfg=self.cfg, betmode=self.betmode)
        self.board.create_board_reelstrips()
        self._update_board_fields()

    def force_board(self, forced_positions: Optional[List[int]] = None):
        if not self.board:
            self.make_board_from_reelstrips()
        self.board.force_board_from_reelstrips(forced_positions)
        self._update_board_fields()

    def _update_board_fields(self):
        self.board_data = self.board.board
        self.last_board = self.board_data
        self.special_symbols_on_board = self.board.special_symbols_on_board
        self.reel_positions = self.board.reel_positions
        self.reelstrip_id = self.board.reelstrip_id
        self.top_padding = self.board.top_symbols
        self.bottom_padding = self.board.bottom_symbols
        self.anticipation = self.board.anticipation

    # --- Book / spin handling ---
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
        entry = dict(description)
        entry["book_id"] = self.book.get("id")
        self.temp_wins.append(entry)

    def finalize_book(self, payout_mult: int) -> Dict[str, Any]:
        self.book["payoutMultiplier"] = int(payout_mult)
        self.totals["spins"] += 1
        if payout_mult > 0:
            self.totals["wins"] += 1
        self.totals["payoutMultSum"] += int(payout_mult)
        self.library.append(dict(self.book))
        return self.book

    def run_spin(self, rng: Rng, evaluator=None) -> Dict[str, Any]:
        from src.evaluator.evaluator import evaluate_board

        # --- Obsługa ForceLoader ---
        if self.force_loader.enabled and self.force_enabled:
            event = self.force_loader.next_event()
            if event:
                payout_mult = int(event.get("payoutMultiplier", 0))
                scatter_wins = int(event.get("scatterWins", 0))
                self.reset_book(criteria=f"{self.cfg.mode}_FORCED")
                self.book["payoutMultiplier"] = payout_mult
                self.book["scatterWins"] = scatter_wins
                self.add_event({"type": "forced_spin", "payoutMultiplier": payout_mult, "scatterWins": scatter_wins})
                return self.finalize_book(payout_mult)

        # --- Normalny spin z Board ---
        self.make_board_from_reelstrips()
        flat_board = [s for row in self.board_data for s in row] if isinstance(self.board_data[0], list) else self.board_data

        # --- Event spin_start ---
        self.reset_book()
        self.add_event({"type": "spin_start", "board": [s.name for s in flat_board], "spins": self.totals["spins"]})

        if evaluator is None:
            evaluator = evaluate_board
        win = evaluator(self.board_data, self.cfg) if evaluator else None
        payout_mult = int(win.get("mult", 0)) if win else 0

        if win and win.get("mult", 0) > 0:
            self.add_event({"type": "line_win", "symbol": win.get("symbol"), "count": win.get("count"), "mult": win.get("mult")})

        # Scatter handling
        scatter_symbol = self.cfg.special_symbols.get("scatter", [None])[0] if self.cfg.special_symbols else None
        scatter_count = sum(1 for s in flat_board if isinstance(s, Symbol) and s.name == scatter_symbol) if scatter_symbol else 0
        scatter_wins = 0
        if scatter_count >= 3:
            self.free_spins += 10
            scatter_wins = scatter_count
            self.add_event({"type": "scatter_event", "symbol": scatter_symbol, "count": scatter_count, "wins": scatter_wins})

        self.book["scatterWins"] = scatter_wins

        # --- Event spin_result ---
        self.add_event({"type": "spin_result", "board": [s.name for s in flat_board], "win": win or {}, "scatterWins": scatter_wins})

        return self.finalize_book(payout_mult)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "last_board": self.last_board,
            "free_spins": self.free_spins,
            "totals": self.totals.copy(),
            "current_book": self.book.copy(),
        }
