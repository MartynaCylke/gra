import sys
from pathlib import Path
from src.state.game_state import GameState
from src.utils.rng import Rng
from src.config.game_configs import cfg_5reel, cfg_3reel  # zakładamy, że masz conftest.py z fixture
from src.evaluator.evaluator import evaluate_board

def run_simulation(cfg_func, betmode_name: str, spins: int = 10, seed: int = 42):
    print(f"Symulacja {betmode_name}...")
    
    # Tworzymy generator losowy
    rng = Rng(seed)

    # Tworzymy GameState
    gs = GameState(cfg=cfg_func())
    gs.sim = 0  # opcjonalnie ustawienie numeru symulacji
    gs.trace = True  # włączamy event trace

    # Symulujemy serie spinów
    for i in range(spins):
        gs.sim = i
        book = gs.run_spin(rng)  # bez argumentu evaluator
        print(f"Spin {i+1}: payoutMultiplier = {book['payoutMultiplier']}, scatterWins = {book['scatterWins']}")

    # Na koniec zapisujemy niestandardowe eventy
    gs.imprint_wins(f"force_record_{betmode_name}.json")
    print(f"Zapisano custom events do force_record_{betmode_name}.json")

if __name__ == "__main__":
    # Symulacja 5-bębnowa
    run_simulation(cfg_5reel, betmode_name="5reel", spins=20)

    # Symulacja 3-bębnowa (opcjonalnie)
    run_simulation(cfg_3reel, betmode_name="3reel", spins=10)
