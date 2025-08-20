import argparse, json
from pathlib import Path
from typing import Iterator, Dict, Any, List

def iter_events(p: Path) -> Iterator[Dict[str, Any]]:
    if p.is_dir():
        p = p / "events.jsonl"
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def is_grid(board: Any) -> bool:
    return isinstance(board, list) and board and isinstance(board[0], list)

def main():
    ap = argparse.ArgumentParser(description="Viewer dla grid_balls (3x5) – pokazuje dolny rząd i WIN/LOSE")
    ap.add_argument("--in", dest="inp", required=True, help="folder z events.jsonl lub ścieżka do pliku")
    ap.add_argument("--limit", type=int, default=20, help="ile spinów wypisać (0 = wszystkie)")
    ap.add_argument("--full", action="store_true", help="pokaż całą planszę (nie tylko dolny rząd)")
    ap.add_argument("--bet", type=float, default=None, help="stawka do obliczenia RTP (opcjonalne)")
    args = ap.parse_args()

    path = Path(args.inp)
    events = list(iter_events(path))
    n = len(events)
    if n == 0:
        print("Brak eventów.")
        return

    wins = 0
    sum_payout = 0.0

    to_show = events if args.limit in (0, None) else events[: args.limit]
    print(f"Pokazuję {len(to_show)} z {n} spinów:\n")

    for e in to_show:
        spin = e.get("spin")
        board = e.get("board")
        win = e.get("win")
        payout = float(e.get("payout", 0))
        sum_payout += payout

        # dolny rząd
        if is_grid(board):
            last_row: List[str] = board[-1]
        else:
            last_row = board if isinstance(board, list) else []

        status = "WIN" if win else "LOSE"
        if status == "WIN":
            wins += 1

        # szczegóły wygranej (jeśli jest)
        details = ""
        if win:
            wtype = win.get("type")
            color = win.get("color")
            mult = win.get("mult")
            details = f" | type={wtype} color={color} mult={mult} payout={payout:g}"

        # wypisz
        line = f"spin={spin:>4}  bottom_row={last_row}  {status}{details}"
        print(line)
        if args.full and is_grid(board):
            print(f"           full_board={board}")

    print("\nPodsumowanie:")
    hit_rate = (wins / n) * 100.0
    print(f"  spiny: {n}")
    print(f"  wygrane: {wins}  (hit-rate: {hit_rate:.2f}%)")
    print(f"  suma wypłat: {sum_payout:g}")
    if args.bet is not None and n > 0:
        rtp = (sum_payout / (args.bet * n)) * 100.0
        print(f"  RTP (przy bet={args.bet}): {rtp:.2f}%")

if __name__ == "__main__":
    main()
