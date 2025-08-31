from src.config.build_config import build_test_config
from src.board.board import Board
from src.utils.rng import Rng

def test_lines_mode():
    rng = Rng(seed=42)
    cfg = build_test_config()
    cfg.mode = "lines"
    betmode = cfg.betmodes[0]  # pierwszy dostępny betmode
    board = Board(cfg=cfg, betmode=betmode, rng=rng)
    board.create_board_reelstrips()
    print("\n=== LINES MODE ===")
    board.print_board()

def test_balls_mode():
    rng = Rng(seed=42)
    cfg = build_test_config()
    cfg.mode = "balls"
    betmode = cfg.betmodes[0]
    board = Board(cfg=cfg, betmode=betmode, rng=rng)
    board.create_board_reelstrips()
    print("\n=== BALLS MODE ===")
    board.print_board()

def test_grid_balls_mode():
    rng = Rng(seed=42)
    cfg = build_test_config()
    cfg.mode = "grid_balls"
    cfg.rows = 3
    cfg.cols = 5
    betmode = cfg.betmodes[0]
    board = Board(cfg=cfg, betmode=betmode, rng=rng)
    board.create_board_reelstrips()
    print("\n=== GRID BALLS MODE ===")
    board.print_board()

def main():
    test_lines_mode()
    test_balls_mode()
    test_grid_balls_mode()

if __name__ == "__main__":
    main()
