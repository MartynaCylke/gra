import argparse, json
from pathlib import Path
from typing import Dict, Any, List
import zstandard as zstd

SCALE = 1_000_000_000_000  # skala uint64 dla prawdopodobieństw

def read_events_jsonl(path: Path):
    if path.is_dir():
        path = path / "events.jsonl"
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)

def to_logic_record(i: int, e: Dict[str, Any], cost: float) -> Dict[str, Any]:
    # payoutMultiplier: preferujemy win.mult; fallback z payout/cost
    pmult = 0
    win = e.get("win")
    if isinstance(win, dict):
        pmult = int(win.get("mult", 0))
    else:
        payout = int(e.get("payout", 0))
        pmult = int(round(payout / cost)) if cost else 0

    minimal_events = [{"board": e.get("board"), "win": win or {}}]
    return {
        "id": i,
        "events": minimal_events,
        "payoutMultiplier": int(pmult),
    }

def write_jsonl_zst(records: List[Dict[str, Any]], out_file: Path):
    cctx = zstd.ZstdCompressor(level=3)
    with cctx.stream_writer(out_file.open("wb")) as compressor:
        for rec in records:
            line = json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n"
            compressor.write(line.encode("utf-8"))

def emit_uniform_csv(n: int, pmults: List[int], out_csv: Path):
    # Jednolite P=1/N w skali SCALE (uint64)
    base = SCALE // n
    rem = SCALE - base * n
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        for i in range(n):
            p = base + (1 if i < rem else 0)
            f.write(f"{i+1},{p},{pmults[i]}\n")

def main():
    ap = argparse.ArgumentParser(description="Eksport do RGS: index.json, lookup.csv, logic.jsonl.zst")
    ap.add_argument("--run", required=True, help="folder z events.jsonl (np. out/runs/kulki_grid_demo)")
    ap.add_argument("--name", default="base", help="nazwa trybu (np. base)")
    ap.add_argument("--cost", type=float, default=1.0, help="koszt rundy (zwykle = bet)")
    ap.add_argument("--out", required=True, help="folder docelowy na pliki RGS")
    args = ap.parse_args()

    run_dir = Path(args.run)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    events = list(read_events_jsonl(run_dir))
    if not events:
        raise SystemExit("Brak events.jsonl w podanym --run albo plik pusty.")

    records, pmults = [], []
    for idx, e in enumerate(events, start=1):
        rec = to_logic_record(idx, e, cost=args.cost)
        records.append(rec)
        pmults.append(rec["payoutMultiplier"])

    logic_name = f"{args.name}.jsonl.zst"
    logic_path = out_dir / logic_name
    write_jsonl_zst(records, logic_path)

    weights_name = f"lookup_{args.name}.csv"
    weights_path = out_dir / weights_name
    emit_uniform_csv(len(records), pmults, weights_path)

    index_path = out_dir / "index.json"
    index = {
        "modes": [
            {
                "name": args.name,
                "cost": float(args.cost),
                "events": logic_name,
                "weights": weights_name,
            }
        ]
    }
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK. Wygenerowano:")
    print(f"- {index_path}")
    print(f"- {weights_path}")
    print(f"- {logic_path}")

if __name__ == "__main__":
    main()
