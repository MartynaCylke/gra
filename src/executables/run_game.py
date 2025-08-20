import argparse
from src.config.build_config import load_config
from src.state.game_state import GameState
from src.calculations.lines import evaluate_single_line
from src.calculations.balls import evaluate_balls
from src.wins.wallet import Wallet
from src.events.events import make_event
from src.write_data.writer import Writer
from src.utils.rng import Rng

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--game", default="0_0_kulki")  # domyślnie nasza gra kulek
    p.add_argument("--spins", type=int, default=20)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out", default="out/runs/kulki_demo")
    args = p.parse_args()

    cfg = load_config(args.game)
    rng = Rng(args.seed)
    state = GameState(cfg)
    wallet = Wallet(cfg)
    writer = Writer(args.out)

    for i in range(args.spins):
        board = state.make_board(rng)
        if cfg.mode == "balls":
            win = evaluate_balls(board, cfg)
        else:
            win = evaluate_single_line(board, cfg)

        payout = wallet.settle(win)
        ev = make_event(i, board, win, payout, wallet.balance, state.snapshot())
        writer.write(ev)

    writer.close()

if __name__ == "__main__":
    main()
