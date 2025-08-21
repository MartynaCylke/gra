from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import argparse, json, csv
import zstandard as zstd

from src.config.build_config import load_config
from src.state.game_state import GameState
from src.utils.rng import Rng
from src.wins.wallet import Wallet
from src.calculations.grid_balls import evaluate_grid_balls
from src.utils.conditions import normalize_conditions


def read_raw_game_json(game_id: str) -> dict:
    p = Path("games") / game_id / "config.json"
    return json.loads(p.read_text(encoding="utf-8"))


def write_books_jsonl(books, out_file: Path, compression: bool):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    if compression:
        cctx = zstd.ZstdCompressor(level=3)
        with cctx.stream_writer(out_file.open("wb")) as w:
            for b in books:
                w.write((json.dumps(b, ensure_ascii=False) + "\n").encode("utf-8"))
    else:
        with out_file.open("w", encoding="utf-8") as f:
            for b in books:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")


def write_lookup_csv(books, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for i, b in enumerate(books, start=1):
            payout = int(b.get("payoutMultiplier", 0))
            w.writerow([i, 1, payout])


def write_id_to_criteria(assignments, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for i, crit in enumerate(assignments, start=1):
            w.writerow([i, crit])


def write_segmented(assignments, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        for i, _ in enumerate(assignments, start=1):
            w.writerow([i, "basegame"])


def write_acceptance_stats(stats: dict, out_json: Path):
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_configs(dir_configs: Path, cfg, bet_cost: float, raw: dict):
    dir_configs.mkdir(parents=True, exist_ok=True)
    (dir_configs / "config.json").write_text(
        json.dumps({"gameId": cfg.id, "betCost": bet_cost}, indent=2), "utf-8")
    (dir_configs / "config_fe.json").write_text(
        json.dumps({"rows": cfg.rows, "cols": cfg.cols, "colors": cfg.colors}, indent=2), "utf-8")
    (dir_configs / "config_math.json").write_text(
        json.dumps({"mode": cfg.mode, "wincap": raw.get("wincap", 0), "bet_modes": raw.get("bet_modes", [])}, indent=2),
        "utf-8",
    )


def build_assignments_interleaved(num_sim: int, distributions: list[dict]) -> list[str]:
    buckets = []
    remaining = num_sim
    for d in distributions:
        q = float(d.get("quota", 0.0))
        take = int(round(q * num_sim))
        take = min(max(take, 0), remaining)
        if take > 0:
            buckets.append([d["criteria"], take])
            remaining -= take
    if remaining > 0:
        last = distributions[-1]["criteria"] if distributions else "basegame"
        buckets.append([last, remaining])
    order = []
    while True:
        progressed = False
        for b in buckets:
            if b[1] > 0:
                order.append(b[0]); b[1] -= 1; progressed = True
        if not progressed:
            break
    return order[:num_sim]


def meets_criteria(pmult: int, criteria: str, raw_cfg: dict, flags: dict | None = None, win_criteria: float | None = None, force_accept: bool = False) -> bool:
    flags = flags or {}
    if force_accept:
        return True
    c = (criteria or "").lower()
    if c in ("wincap", "win_cap", "win cap", "max-win", "maxwin"):
        target = int(win_criteria or raw_cfg.get("wincap", 0) or raw_cfg.get("rules", {}).get("bottom_row_all_same", 0))
        return pmult >= target
    if c in ("0", "zero", "lose"):
        return pmult == 0
    if c == "basegame":
        return pmult > 0 and not flags.get("freegame_triggered", False)
    if c == "freegame":
        return bool(flags.get("freegame_triggered", False))
    return True


def simulate_mode(mode_name: str, num_sim: int, distributions: list[dict], seed: int, cfg, raw, lib_dir: Path, compression: bool):
    state = GameState(cfg, trace=False)
    wallet = Wallet(cfg)
    books = []

    events_path = lib_dir / "books" / f"events_{mode_name}.jsonl"
    with events_path.open("w", encoding="utf-8") as ef:
        assignments = build_assignments_interleaved(num_sim, distributions)

        attempts_sum = 0
        attempts_max = 0
        target_counts = {}
        for c in assignments:
            target_counts[c] = target_counts.get(c, 0) + 1

        for i, dist in enumerate(distributions, start=1):
            pass  # placeholder to satisfy linter (not used directly)

        # dla każdego ID – wiemy, jakie criteria; szukamy pasującego Distribution (po nazwie)
        # jeśli jest kilka o tym samym criteria – użyjemy pierwszej
        crit_to_dist = {}
        for d in distributions:
            key = (d.get("criteria") or "").lower()
            if key and key not in crit_to_dist:
                crit_to_dist[key] = d

        for i, crit in enumerate(assignments, start=1):
            d = crit_to_dist.get((crit or "").lower(), {})
            cond = normalize_conditions(d.get("conditions"))
            win_crit = d.get("win_criteria")

            attempt = 0
            while True:
                rng = Rng(seed + i * 10007 + attempt)
                state.reset_book(criteria=crit)
                board = state.make_board(rng)
                win = evaluate_grid_balls(board, cfg)
                pmult = int(win.get("mult", 0)) if win else 0

                flags = {"freegame_triggered": bool(cond["force_freegame"])}
                force_accept = bool(cond["force_wincap"]) and (crit.lower() in ("wincap","win_cap","max-win","maxwin"))

                if meets_criteria(pmult, crit, raw, flags, win_criteria=win_crit, force_accept=force_accept) or attempt > 1000:
                    state.finalize_book(pmult)
                    books.append(dict(state.book))
                    payout = wallet.settle(win or {})
                    ef.write(json.dumps(
                        {"id": i, "mode": mode_name, "criteria": crit, "board": board, "win": win, "payout": payout},
                        ensure_ascii=False
                    ) + "\n")
                    attempts_sum += (attempt + 1)
                    attempts_max = max(attempts_max, attempt + 1)
                    break
                attempt += 1

    logic_path = (lib_dir / "books_compressed" / f"books_{mode_name}.jsonl.zst") if compression \
                 else (lib_dir / "books" / f"books_{mode_name}.jsonl")
    write_books_jsonl(books, logic_path, compression=compression)

    write_lookup_csv(books, lib_dir / "lookup_tables" / f"lookUpTable_{mode_name}.csv")
    write_id_to_criteria(assignments, lib_dir / "lookup_tables" / f"lookUpTableIdToCriteria_{mode_name}.csv")
    write_segmented(assignments, lib_dir / "lookup_tables" / f"lookUpTableSegmented_{mode_name}.csv")

    stats = {
        "mode": mode_name,
        "N": len(books),
        "target_counts": target_counts,
        "attempts": {"avg": (attempts_sum / len(books)) if books else 0.0, "max": attempts_max},
    }
    write_acceptance_stats(stats, lib_dir / "lookup_tables" / f"acceptance_stats_{mode_name}.json")

    return {"logic_path": str(logic_path), "N": len(books)}


def main():
    ap = argparse.ArgumentParser(description="0_0_kulki run-file (multi-mode) z Acceptance Criteria & BetMode conditions")
    ap.add_argument("--num_sim", type=int, default=1000, help="liczba symulacji na BetMode")
    ap.add_argument("--seed", type=int, default=123, help="seed bazowy RNG")
    ap.add_argument("--compression", type=lambda x: str(x).lower() in ("1","true","yes"), default=True)
    args = ap.parse_args()

    game_id = "0_0_kulki"
    raw = read_raw_game_json(game_id)
    cfg = load_config(game_id)

    lib_dir = Path("games") / game_id / "library"
    for sub in ("books","books_compressed","lookup_tables","configs","forces"):
        (lib_dir / sub).mkdir(parents=True, exist_ok=True)

    generate_configs(lib_dir / "configs", cfg, bet_cost=float(cfg.bet), raw=raw)

    betmodes = raw.get("bet_modes", [
        {"name": "base", "cost": float(cfg.bet), "distributions": [{"criteria":"basegame","quota":1.0}]}
    ])

    results = []
    for bm in betmodes:
        mode_name = bm.get("name", "base")
        distributions = bm.get("distributions", [{"criteria":"basegame","quota":1.0}])
        res = simulate_mode(mode_name, args.num_sim, distributions, args.seed, cfg, raw, lib_dir, args.compression)
        results.append((mode_name, res["logic_path"], res["N"]))

    print("OK. Zapisano do:", lib_dir)
    for mode_name, logic_path, N in results:
        print(f" - [{mode_name}] {logic_path} (N={N})")
        print(f"   lookup_tables/lookUpTable_{mode_name}.csv")
        print(f"   lookup_tables/lookUpTableIdToCriteria_{mode_name}.csv")
        print(f"   lookup_tables/lookUpTableSegmented_{mode_name}.csv")
        print(f"   lookup_tables/acceptance_stats_{mode_name}.json")
    print(" - configs/ (config.json, config_fe.json, config_math.json)")


if __name__ == "__main__":
    main()
