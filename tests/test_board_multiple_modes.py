from src.config.build_config import build_test_config
from src.board.board import Board
from src.utils.rng import Rng

def test_lines_mode(rng: Rng):
    cfg = build_test_config()
    cfg.mode = "lines"
    board = Board(cfg=cfg, betmode=cfg.betmodes[0], rng=rng)
    board.create_board_reelstrips()
    print("\n=== LINES MODE ===")
    board.print_board()

def test_balls_mode(rng: Rng):
    cfg = build_test_config()
    cfg.mode = "balls"
    board = Board(cfg=cfg, betmode=cfg.betmodes[0], rng=rng)
    board.create_board_reelstrips()
    print("\n=== BALLS MODE ===")
    board.print_board()

def test_grid_balls_mode(rng: Rng):
    cfg = build_test_config()
    cfg.mode = "grid_balls"
    cfg.rows = 3
    cfg.cols = 5
    board = Board(cfg=cfg, betmode=cfg.betmodes[0], rng=rng)
    board.create_board_reelstrips()
    print("\n=== GRID BALLS MODE ===")
    board.print_board()

def main():
    rng = Rng(seed=42)  # ustalamy seed, żeby wyniki były powtarzalne
    test_lines_mode(rng)
    test_balls_mode(rng)
    test_grid_balls_mode(rng)

if __name__ == "__main__":
    main()
