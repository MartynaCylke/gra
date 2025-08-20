import argparse, json
from pathlib import Path
from src.config.build_config import load_config
from src.state.game_state import GameState
from src.wins.wallet import Wallet
from src.events.events import make_event
from src.write_data.writer import Writer
from src.utils.rng import Rng
from src.calculations.grid_balls import evaluate_grid_balls  # dla grid_balls

def main():
    p = argparse.ArgumentParser(description="Game runner")
    p.add_argument("--game", default="0_0_kulki", help="ID gry (folder w games/)")
    p.add_argument("--spins", type=int, default=20, help="liczba spinów do symulacji")
    p.add_argument("--seed", type=int, default=42, help="seed RNG dla powtarzalności")
    p.add_argument("--out", default="out/runs/demo", help="folder wyjściowy na wyniki")
    p.add_argument("--trace", action="store_true", help="zapisuj eventy do Book")
    args = p.parse_args()

    cfg = load_config(args.game)
    rng = Rng(args.seed)
    state = GameState(cfg, trace=args.trace)
    wallet = Wallet(cfg)
    writer = Writer(args.out)

    # tylko jeden betmode (base); w przyszłości pętla po cfg.betmodes
    for i in range(args.spins):
        # wybór evaluatora wg trybu
        if cfg.mode == "grid_balls":
            book = state.run_spin(rng, evaluator=evaluate_grid_balls)
            # dla zgodności z istniejącym events.jsonl
            board = state.book["events"][0]["board"] if state.book["events"] else None
            win = state.book["events"][0]["win"] if state.book["events"] else None
        elif cfg.mode == "balls":
            from src.calculations.balls import evaluate_balls
            book = state.run_spin(rng, evaluator=evaluate_balls)
            board = state.book["events"][0]["board"] if state.book["events"] else None
            win = state.book["events"][0]["win"] if state.book["events"] else None
        else:
            from src.calculations.lines import evaluate_single_line
            # ręcznie dla lines (board = lista 3 symboli)
            state.reset_book(criteria=cfg.mode)
            board = state.make_board(rng)
            win = evaluate_single_line(board, cfg)
            payout_mult = int(win.get("mult", 0)) if win else 0
            book = state.finalize_book(payout_mult)

        payout = wallet.settle(win if win else {})
        ev = make_event(i, board, win, payout, wallet.balance, state.snapshot())
        writer.write(ev)

    writer.close()

    # Zapisz Library jako books.jsonl (format “Book” zgodny z opisem)
    books_path = Path(args.out) / "books.jsonl"
    with books_path.open("w", encoding="utf-8") as f:
        for b in state.library:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")

    # Krótkie podsumowanie
    print(f"Spiny: {state.totals['spins']}, Wygrane: {state.totals['wins']}, Suma mult: {state.totals['payoutMultSum']}")
    print(f"Books zapisane do: {books_path}")

if __name__ == "__main__":
    main()
