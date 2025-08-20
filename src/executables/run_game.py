import argparse
from src.config.build_config import load_config
from src.state.game_state import GameState
from src.wins.wallet import Wallet
from src.events.events import make_event
from src.write_data.writer import Writer
from src.utils.rng import Rng
from src.calculations.grid_balls import evaluate_grid_balls  # nowy evaluator 3x5 (dolny rząd)

def main():
    p = argparse.ArgumentParser(description="Game runner")
    p.add_argument("--game", default="0_0_kulki", help="ID gry (folder w games/)")
    p.add_argument("--spins", type=int, default=20, help="liczba spinów do symulacji")
    p.add_argument("--seed", type=int, default=42, help="seed RNG dla powtarzalności")
    p.add_argument("--out", default="out/runs/demo", help="folder wyjściowy na wyniki")
    args = p.parse_args()

    cfg = load_config(args.game)
    rng = Rng(args.seed)
    state = GameState(cfg)
    wallet = Wallet(cfg)
    writer = Writer(args.out)

    for i in range(args.spins):
        board = state.make_board(rng)

        if cfg.mode == "grid_balls":
            # Siatka 3x5 – wygrana tylko, gdy dolny rząd ma 5 takich samych kolorów
            win = evaluate_grid_balls(board, cfg)
        elif cfg.mode == "balls":
            # Stary tryb: 3 kulki w linii
            from src.calculations.balls import evaluate_balls
            win = evaluate_balls(board, cfg)
        else:
            # Tryb linii (3 bębny)
            from src.calculations.lines import evaluate_single_line
            win = evaluate_single_line(board, cfg)

        payout = wallet.settle(win)
        ev = make_event(i, board, win, payout, wallet.balance, state.snapshot())
        writer.write(ev)

    writer.close()

if __name__ == "__main__":
    main()
