import argparse
import json
from pathlib import Path

from src.config.build_config import load_config
from src.state.game_state import GameState
from src.wins.wallet import Wallet
from src.events.events import make_event
from src.write_data.writer import Writer
from src.utils.rng import Rng

# Evaluatory mechanik
from src.calculations.grid_balls import evaluate_grid_balls  # grid 3x5 (liczy się dolny rząd)
from src.calculations.balls import evaluate_balls            # stary tryb 3 kulki
from src.calculations.lines import evaluate_single_line      # 3-bębnowy fallback
# 5-bębnowy evaluator (upewnij się, że masz plik src/calculations/lines5.py zgodnie z wcześniejszym krokiem)
try:
    from src.calculations.lines5 import evaluate_lines_5reel
except Exception:
    evaluate_lines_5reel = None


def main():
    p = argparse.ArgumentParser(description="Game runner (grid_balls / balls / lines with 5-reel support)")
    p.add_argument("--game", default="0_0_kulki", help="ID gry (folder w games/)")
    p.add_argument("--spins", type=int, default=20, help="liczba spinów do symulacji")
    p.add_argument("--seed", type=int, default=42, help="seed RNG dla powtarzalności")
    p.add_argument("--out", default="out/runs/demo", help="folder wyjściowy na wyniki")
    args = p.parse_args()

    cfg = load_config(args.game)
    rng = Rng(args.seed)
    # Włączamy trace=True, by Book zawierał eventy (ułatwia zapis do books.jsonl)
    state = GameState(cfg, trace=True)
    wallet = Wallet(cfg)
    writer = Writer(args.out)

    for i in range(args.spins):
        # 1) Zbuduj board
        board = state.make_board(rng)

        # 2) Wybierz evaluator wg trybu
        if cfg.mode == "grid_balls":
            win = evaluate_grid_balls(board, cfg)
        elif cfg.mode == "balls":
            win = evaluate_balls(board, cfg)
        else:
            # Tryb lines: jeśli mamy 5 symboli w board, użyj 5-bębnowego evaluatora
            if isinstance(board, list) and len(board) >= 5 and evaluate_lines_5reel is not None:
                win = evaluate_lines_5reel(board, cfg)
            else:
                win = evaluate_single_line(board, cfg)

        # 3) Rozlicz portfel
        payout = wallet.settle(win or {})

        # 4) Zapis eventu do pliku zdarzeń
        ev = make_event(i, board, win, payout, wallet.balance, state.snapshot())
        writer.write(ev)

        # 5) Zapis Book-a (State Machine)
        state.reset_book(criteria=cfg.mode)
        state.add_event({"board": board, "win": win or {}})
        payout_mult = int(win.get("mult", 0)) if win else 0
        state.finalize_book(payout_mult)

    writer.close()

    # 6) Zapisz bibliotekę Book-ów (books.jsonl) w folderze wyjściowym
    books_path = Path(args.out) / "books.jsonl"
    with books_path.open("w", encoding="utf-8") as f:
        for b in state.library:
            f.write(json.dumps(b, ensure_ascii=False) + "\n")

    # 7) Podsumowanie
    print(f"Spiny: {state.totals['spins']}, Wygrane: {state.totals['wins']}, Suma mult: {state.totals['payoutMultSum']}")
    print(f"Books zapisane do: {books_path}")


if __name__ == "__main__":
    main()
