import sys
from pathlib import Path
from src.state.game_state import GameState
from src.utils.rng import Rng
from src.config.game_configs import cfg_5reel, cfg_3reel
from src.evaluator.evaluator import evaluate_board
import json


def run_simulation(cfg, betmode_name: str, spins: int = 10, seed: int = 42):
    print(f"Symulacja {betmode_name}...")

    # Wczytaj force.json
    try:
        with open("force.json", "r") as f:
            forced_spins = json.load(f)
        print(f"[ForceLoader] Załadowano {len(forced_spins)} wymuszonych spinów z force.json")
    except FileNotFoundError:
        forced_spins = []
        print("[ForceLoader] Brak pliku force.json, lecimy losowo")

    rng = Rng(seed)
    gs = GameState(cfg=cfg)
    gs.sim = 0
    gs.trace = True

    for i in range(spins):
        gs.sim = i

        if i < len(forced_spins):
            # Spin wymuszony z force.json
            book = forced_spins[i]
            print(f"[FORCE] Spin {i+1}: payout={book.get('payoutMultiplier', 0)}, scatters={book.get('scatterWins', 0)}")
        else:
            # Normalny spin losowy
            book = gs.run_spin(rng)

        print(f"Spin {i+1}: payoutMultiplier = {book['payoutMultiplier']}, scatterWins = {book['scatterWins']}")

    # Zapisz niestandardowe eventy
    gs.imprint_wins(f"force_record_{betmode_name}.json")
    print(f"Zapisano custom events do force_record_{betmode_name}.json")


if __name__ == "__main__":
    # Symulacja 5-bębnowa
    run_simulation(cfg_5reel, betmode_name="5reel", spins=20)

    # Symulacja 3-bębnowa
    run_simulation(cfg_3reel, betmode_name="3reel", spins=10)
