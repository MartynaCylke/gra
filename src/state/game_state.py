from dataclasses import dataclass
from typing import List, Union
from src.config.build_config import GameConfig
from src.utils.rng import Rng

BoardType = Union[List[str], List[List[str]]]

@dataclass
class GameState:
    cfg: GameConfig

    def make_board(self, rng: Rng) -> BoardType:
        if self.cfg.mode == "grid_balls":
            assert self.cfg.colors and self.cfg.rows and self.cfg.cols
            return [
                [rng.choice_weighted(self.cfg.colors, self.cfg.weights) for _ in range(self.cfg.cols)]
                for _ in range(self.cfg.rows)
            ]
        if self.cfg.mode == "balls":
            # stary tryb: 3 kulki w linii
            assert self.cfg.colors
            return [rng.choice_weighted(self.cfg.colors, self.cfg.weights) for _ in range(3)]
        # lines (3 bębny)
        assert self.cfg.reels, "Brak 'reels' w configu gry lines"
        return [rng.choice(reel) for reel in self.cfg.reels]

    def snapshot(self):
        return {}

