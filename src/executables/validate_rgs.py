import json, io, csv
from pathlib import Path
import zstandard as zstd

SCALE = 1_000_000_000_000

def load_index(dir_path: Path):
    idx = json.loads((dir_path / "index.json").read_text(encoding="utf-8"))
    assert "modes" in idx and isinstance(idx["modes"], list) and len(idx["modes"]) >= 1
    return idx

def check_mode(dir_path: Path, mode: dict):
    events_file = dir_path / mode["events"]
    weights_file = dir_path / mode["weights"]
    assert events_file.exists(), f"Brak: {events_file}"
    assert weights_file.exists(), f"Brak: {weights_file}"

    # read pmults from jsonl.zst
    dctx = zstd.ZstdDecompressor()
    pm_json = []
    with dctx.stream_reader(events_file.open("rb")) as r:
        text = io.TextIOWrapper(r, encoding="utf-8")
        for line in text:
            if line.strip():
                rec = json.loads(line)
                for k in ("id", "events", "payoutMultiplier"):
                    assert k in rec, f"Brak klucza {k} w logic"
                pm_json.append(int(rec["payoutMultiplier"]))
    n = len(pm_json)
    assert n > 0, "Brak rekordów w logic"

    # read CSV: id,probability_uint64,payout
    pm_csv = []
    prob_sum = 0
    with weights_file.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.reader(f)
        for row in rdr:
            assert len(row) == 3, "CSV musi mieć 3 kolumny"
            _id = int(row[0]); prob = int(row[1]); pm = int(row[2])
            pm_csv.append(pm)
            prob_sum += prob
    assert len(pm_csv) == n, "Liczba rekordów w CSV ≠ logic"
    assert pm_csv == pm_json, "payoutMultiplier w CSV ≠ logic"
    assert prob_sum == SCALE, f"Suma prawdopodobieństw musi wynosić {SCALE}, a jest {prob_sum}"

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="folder z index.json")
    args = ap.parse_args()
    d = Path(args.dir)
    idx = load_index(d)
    for m in idx["modes"]:
        check_mode(d, m)
    print("OK: pliki zgodne z wymaganiami Math verification")

if __name__ == "__main__":
    main()
