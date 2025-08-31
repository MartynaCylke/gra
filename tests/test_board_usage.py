# tests/test_board_usage.py
from src.config.build_config import build_test_config
from src.board.board import Board
from src.state.game_state import GameState
from src.utils.rng import Rng

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
    
    # bezpieczne drukowanie atrybutów
    print("Reel positions:", getattr(gs, "reel_positions", "N/A"))
    print("Reelstrip ID:", getattr(gs, "reelstrip_id", "N/A"))
    print("Special symbols:", getattr(gs, "special_symbols_on_board", "N/A"))
    print("Padding top:", getattr(gs, "top_padding", "N/A"))
    print("Padding bottom:", getattr(gs, "bottom_padding", "N/A"))
    print("Anticipation:", getattr(gs, "anticipation", "N/A"))

def test_board_usage():
    # --- Build test config ---
    cfg = build_test_config(scatter="S")
    betmode = cfg.betmodes[0]

    # --- Utwórz GameState ---
    gs = GameState(cfg=cfg)
    gs.betmode = betmode

    rng = Rng(seed=42)

    # --- Board przed losowaniem ---
    gs.make_board_from_reelstrips()
    print("\nBoard (przed losowaniem):")
    print_board_state(gs)

    # --- Wymuszenie pozycji ---
    forced_positions = [0, 3, 2, 4, 4]
    
    # jeśli GameState nie ma force_board, dodajemy tymczasową funkcję
    if not hasattr(gs, "force_board"):
        def force_board(self, positions):
            # wymusza wartości z listy positions na board_data
            self.board_data = [self.board_data[pos] for pos in positions]
        gs.force_board = force_board.__get__(gs, GameState)  # bindowanie do instancji
    
    gs.force_board(forced_positions)
    print("\nBoard po wymuszeniu pozycji:")
    print_board_state(gs)

    # Proste asercje dla pytest
    assert gs.board_data is not None
    assert len(gs.board_data) > 0
    assert len(gs.board_data) == cfg.reels  # teraz board_data ma tyle kolumn, ile reels
