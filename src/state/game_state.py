from dataclasses import dataclass
from typing import List
from src.config.build_config import GameConfig
from src.utils.rng import Rng

@dataclass
class GameState:
    cfg: GameConfig

    def make_board(self, rng: Rng) -> List[str]:
        # Tryb kulek: losujemy 3 kolory z wagami (zwracamy listę 3 symboli-kolorów)
        if self.cfg.mode == "balls":
            assert self.cfg.colors, "Brak 'colors' w configu gry balls"
            return [rng.choice_weighted(self.cfg.colors, self.cfg.weights) for _ in range(3)]

        # Tryb lines (3 bębny -> po 1 symbolu z każdego)
        assert self.cfg.reels, "Brak 'reels' w configu gry lines"
        return [rng.choice(reel) for reel in self.cfg.reels]

    def snapshot(self):
        return {}
