# tests/test_board_usage.py
import sys
from pathlib import Path

# dodaj src do sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from src.config.build_config import build_test_config
from src.board.board import Board
from src.state.game_state import GameState
from src.utils.rng import Rng

def main():
    # --- Build test config ---
    cfg = build_test_config(scatter="S")
    betmode = cfg.betmodes[0]

    # --- Utwórz GameState ---
    gs = GameState(cfg=cfg)
    gs.betmode = betmode

    rng = Rng(seed=42)

    # --- Board przed losowaniem ---
    print("Board (przed losowaniem):")
    gs.make_board_from_reelstrips()
    print_board_state(gs)

    # --- Wymuszenie pozycji ---
    forced_positions = [0, 3, 2, 4, 4]
    gs.force_board(forced_positions)
    print("\nBoard po wymuszeniu pozycji:")
    print_board_state(gs)

def print_board_state(gs: GameState):
    if not gs.board_data:
        print("Board jest pusty")
        return
    # drukuj board
    if isinstance(gs.board_data[0], list):
        for row in gs.board_data:
            print(" ".join(s.name for s in row))
    else:
        print(" ".join(s.name for s in gs.board_data))
    print("Reel positions:", gs.reel_positions)
    print("Reelstrip ID:", gs.reelstrip_id)
    print("Special symbols:", gs.special_symbols_on_board)
    print("Padding top:", gs.top_padding)
    print("Padding bottom:", gs.bottom_padding)
    print("Anticipation:", gs.anticipation)

if __name__ == "__main__":
    main()
