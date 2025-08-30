from typing import List, Dict, Any, Optional
from src.symbol.symbol import Symbol
from src.utils.rng import Rng


class Board:
    def __init__(self, cfg, betmode, rng: Rng):
        self.cfg = cfg
        self.betmode = betmode
        self.rng = rng  # używany RNG przekazany z zewnątrz

        self.rows = cfg.rows or 3
        self.cols = cfg.cols or 5
        self.include_padding = getattr(cfg, "include_padding", False)

        # Padding top/bottom jeśli include_padding = True
        self.padding_top: List[Symbol] = [
            Symbol(cfg, self.rng.choice(cfg.colors)) for _ in range(self.cols)
        ] if self.include_padding else []

        self.padding_bottom: List[Symbol] = [
            Symbol(cfg, self.rng.choice(cfg.colors)) for _ in range(self.cols)
        ] if self.include_padding else []

        # 2D board
        self.board: List[List[Symbol]] = []

        # Specjalne symbole na planszy
        self.special_symbols_on_board: Dict[str, List[Dict[str, int]]] = {}

        # Reel positions
        self.reel_positions: List[int] = []
        self.reelstrip_id: Optional[str] = None

        # Anticipation
        self.anticipation: List[int] = []

    def create_board_reelstrips(self):
        # Pobranie warunków z betmode
        conds_list = self.betmode.get_distribution_conditions()
        if not conds_list:
            raise ValueError("Brak warunków w betmode")
        conds = conds_list[0]

        # Wybór reelstrip ID (tu prosta implementacja, default)
        self.reelstrip_id = "default"

        # Generowanie losowych reel_positions
        self.reel_positions = [
            self.rng.randint(0, len(self.cfg.reels[c]) - 1) for c in range(self.cols)
        ]

        # Tworzenie planszy
        self.board = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                reel = self.cfg.reels[c]
                pos = (self.reel_positions[c] + r) % len(reel)
                row.append(Symbol(self.cfg, reel[pos]))
            self.board.append(row)

        # Skany specjalnych symboli
        self.special_symbols_on_board = {}
        for prop, symbols in self.cfg.special_symbols.items():
            self.special_symbols_on_board[prop] = []
            for r, row in enumerate(self.board):
                for c, sym in enumerate(row):
                    if sym.name in symbols:
                        self.special_symbols_on_board[prop].append({"row": r, "reel": c})

        # Anticipation
        scatter_needed = 3
        scatter_count = len(self.special_symbols_on_board.get("scatter", []))
        self.anticipation = [
            max(0, scatter_needed - scatter_count - i) for i in range(self.cols)
        ]

    def force_board_from_reelstrips(self, forced_positions: Optional[List[int]] = None):
        if forced_positions:
            if len(forced_positions) != self.cols:
                raise ValueError("Lista forced_positions musi mieć długość cols")
            self.reel_positions = forced_positions
        self.create_board_reelstrips()

    def print_board(self):
        for row in self.board:
            print(" ".join([s.name for s in row]))
