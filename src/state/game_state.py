# src/state/game_state.py
from src.board.board import Board
from src.symbol.symbol import Symbol
from src.utils.rng import Rng

class GameState:
    def __init__(self, cfg, betmode=None, trace=False, free_spins=0):
        self.cfg = cfg
        self.betmode = betmode
        self.trace = trace
        self.free_spins = free_spins

        # Board state
        self.board_data = None
        self.last_board = None
        self.reel_positions = [0] * cfg.reels
        self.reelstrip_id = None
        self.special_symbols_on_board = []
        self.top_padding = 0
        self.bottom_padding = 0
        self.anticipation = []

        # Event book
        self.book = {"events": []}

        # Force loader flag (np. do testów)
        self.force_loader = type('ForceLoader', (), {'enabled': True})()

    # -----------------------
    # Board methods
    # -----------------------
    def make_board_from_reelstrips(self):
        """Losuje board na podstawie reelstripów i aktualizuje reel_positions"""
        self.board_data = []
        for r in range(self.cfg.reels):
            pos = Rng().randint(0, len(self.cfg.reelstrips[r])-1)
            self.reel_positions[r] = pos
            symbol = Symbol(self.cfg, self.cfg.reelstrips[r][pos])
            self.board_data.append(symbol)
        self._update_board_metadata()

    def force_board(self, positions):
        """Wymusza konkretne pozycje z reelstripów"""
        self.board_data = []
        for r, pos in enumerate(positions):
            self.reel_positions[r] = pos
            symbol = Symbol(self.cfg, self.cfg.reelstrips[r][pos])
            self.board_data.append(symbol)
        self._update_board_metadata()

    def _update_board_metadata(self):
        """Aktualizuje metadata boardu"""
        self.special_symbols_on_board = [s.name for s in self.board_data if s.name in getattr(self.cfg, 'special_symbols', [])]
        self.top_padding = 0
        self.bottom_padding = 0
        self.anticipation = []

    # -----------------------
    # Event methods
    # -----------------------
    def add_event(self, event):
        """Dodaje event do book"""
        self.book.setdefault("events", []).append(event)

    # -----------------------
    # Spin methods
    # -----------------------
    def run_spin(self, rng=None, evaluator=None):
        """
        Wykonuje spin.
        - rng: instancja Rng lub DummyRng
        - evaluator: funkcja do oceny boardu (np. evaluate_single_line)
        """
        # Losowanie boardu jeśli nie ustawiony
        if self.board_data is None or not self.force_loader.enabled:
            self.make_board_from_reelstrips()

        # Zapamiętanie ostatniego boardu
        self.last_board = self.board_data.copy()

        # Event: spin start
        self.add_event({"type": "spin_start"})

        # Ocena boardu
        win = None
        if evaluator:
            try:
                # Obsługa 1D i 2D board_data
                board_eval = self.board_data
                if isinstance(board_eval[0], list):
                    # jeśli 2D (multirow), spłaszczamy do 1D dla evaluator
                    board_eval_flat = [s for row in board_eval for s in row]
                    win = evaluator(board_eval_flat, self.cfg)
                else:
                    win = evaluator(board_eval, self.cfg)
            except Exception as e:
                print("Błąd evaluator:", e)

        # Obsługa freespins
        if hasattr(self.cfg, "scatter") and self.cfg.scatter in [s.name for s in self.board_data]:
            # uproszczone: 3+ scatter = +10 freespins
            scatter_count = sum(1 for s in self.board_data if s.name == self.cfg.scatter)
            if scatter_count >= 3:
                self.free_spins += 10
                self.add_event({"type": "freespin_update", "value": self.free_spins})

        # Event: spin result
        self.add_event({"type": "spin_result", "win": win, "board": self.board_data})

        return {"board": self.board_data, "win": win, "events": self.book.get("events", [])}

    # -----------------------
    # Reset / utility
    # -----------------------
    def reset_book(self, criteria=None):
        self.book = {"events": []}

