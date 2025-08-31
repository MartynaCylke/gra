from typing import List, Dict, Optional
from src.symbol import Symbol
from src.utils.rng import Rng


class Board:
    def __init__(self, cfg, betmode, rng: Rng):
        self.cfg = cfg
        self.betmode = betmode
        self.rng = rng

        # liczba wierszy i kolumn
        self.rows = getattr(cfg, "rows", 3) or 3
        self.cols = getattr(cfg, "cols", 5) or 5
        self.include_padding = getattr(cfg, "include_padding", False)

        # sprawdzanie reelstripów
        if not getattr(cfg, "reels", None) or len(cfg.reels) < self.cols:
            raise ValueError(f"Liczba reelstripów ({len(cfg.reels) if cfg.reels else 0}) musi być >= cols ({self.cols})")

        # opcjonalne dodatkowe symbole na górze i dole planszy
        self.top_symbols: List[Symbol] = [
            Symbol(cfg, self.rng.choice(cfg.colors)) for _ in range(self.cols)
        ] if self.include_padding else []

        self.bottom_symbols: List[Symbol] = [
            Symbol(cfg, self.rng.choice(cfg.colors)) for _ in range(self.cols)
        ] if self.include_padding else []

        self.board: List[List[Symbol]] = []
        self.special_symbols_on_board: Dict[str, List[Dict[str, int]]] = {}
        self.reel_positions: List[int] = []
        self.reelstrip_id: Optional[str] = None
        self.anticipation: List[int] = []

    def create_board_reelstrips(self):
        # pobranie warunków dystrybucji
        conds_list = self.betmode.get_distribution_conditions()
        if not conds_list:
            conds_list = [{}]  # zapobiega ValueError

        self.reelstrip_id = "default"

        # losowanie pozycji reelstripów
        self.reel_positions = [
            self._safe_randint(0, len(self.cfg.reels[c]) - 1) for c in range(self.cols)
        ]

        # tworzenie planszy (2D list)
        self.board = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                reel = self.cfg.reels[c]
                pos = (self.reel_positions[c] + r) % len(reel)
                row.append(Symbol(self.cfg, reel[pos]))
            self.board.append(row)

        # oznaczanie symboli specjalnych
        self.special_symbols_on_board = {}
        for prop, symbols in getattr(self.cfg, "special_symbols", {}).items():
            self.special_symbols_on_board[prop] = []
            for r, row in enumerate(self.board):
                for c, sym in enumerate(row):
                    if sym.name in symbols:
                        self.special_symbols_on_board[prop].append({"row": r, "reel": c})

        # anticipacja dla scatterów
        scatter_needed = 3
        scatter_count = len(self.special_symbols_on_board.get("scatter", []))
        self.anticipation = [
            max(0, scatter_needed - scatter_count - i) for i in range(self.cols)
        ]

    def force_board_from_reelstrips(self, forced_positions: Optional[List[int]] = None):
        if forced_positions:
            if len(forced_positions) != self.cols:
                raise ValueError("Lista forced_positions musi mieć długość cols")
            # upewniamy się, że są inty
            self.reel_positions = [int(p) for p in forced_positions]
        self.create_board_reelstrips()

    def _safe_randint(self, start: int, end: int) -> int:
        """Obsługa DummyRng lub standardowego Rng, zawsze zwraca int."""
        val = self.rng.randint(start, end)
        try:
            return int(val)
        except (ValueError, TypeError):
            # jeśli rng zwraca symbol, losujemy index w reel
            reel_length = end - start + 1
            if isinstance(val, str) and hasattr(self.cfg, "reels"):
                # znajdź index symbolu w pierwszym reel
                for c in range(len(self.cfg.reels)):
                    if val in self.cfg.reels[c]:
                        return self.cfg.reels[c].index(val)
            # fallback: losowy index
            from random import randint
            return randint(start, end)

    def print_board(self):
        for row in self.board:
            print(" ".join([s.name for s in row]))
