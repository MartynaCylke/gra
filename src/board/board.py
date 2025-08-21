from typing import List, Dict, Any
import random
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol

class Board:
    def __init__(self, cfg: GameConfig):
        self.cfg = cfg
        self.rows = cfg.rows or 3
        self.cols = cfg.cols or 5
        self.include_padding = getattr(cfg, "include_padding", False)

        # Top i bottom symbols jeśli include_padding = True
        self.top_symbols: List[Symbol] = [
            Symbol(name=random.choice(cfg.colors), config=cfg) for _ in range(self.cols)
        ] if self.include_padding else []

        self.bottom_symbols: List[Symbol] = [
            Symbol(name=random.choice(cfg.colors), config=cfg) for _ in range(self.cols)
        ] if self.include_padding else []

        # 2D plansza
        self.board: List[List[Symbol]] = self._generate_board()

        # Special symbols na planszy
        self.special_symbols_on_board: Dict[str, List[Dict[str, int]]] = self._scan_special_symbols()

    def _generate_board(self) -> List[List[Symbol]]:
        board = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                sym_name = random.choice(self.cfg.colors)  # używamy colors, nie symbols
                row.append(Symbol(name=sym_name, config=self.cfg))  # teraz przekazujemy config
            board.append(row)
        return board

    def _scan_special_symbols(self) -> Dict[str, List[Dict[str, int]]]:
        special_symbols_on_board = {}
        special_cfg = getattr(self.cfg, "special_symbols", {}) or {}
        for prop, symbols in special_cfg.items():
            special_symbols_on_board[prop] = []
            for r, row in enumerate(self.board):
                for c, sym in enumerate(row):
                    if sym.name in symbols:
                        special_symbols_on_board[prop].append({"row": r, "reel": c})
        return special_symbols_on_board

    def print_board(self, board: List[List[Symbol]] = None):
        if board is None:
            board = self.board
        for row in board:
            print(" ".join([s.name for s in row]))
