import json
from src.state.game_state import GameState
from src.utils.dummy_rng import DummyRng
from src.config.build_config import GameConfig, Paytable

NUM_SPINS = 10000  # liczba spinów do symulacji

# ---------------- CONFIG FUNCTIONS ----------------
def get_cfg_5reel() -> GameConfig:
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
        ],
        paytable=Paytable(
            three_kind={"A": 10, "B": 5, "C": 3},
            four_kind={"A": 20, "B": 10, "C": 6},
            five_kind={"A": 50, "B": 25, "C": 15}
        ),
        special_symbols={"wild": ["W"]},
    )

def get_cfg_3reel() -> GameConfig:
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "S"],
            ["A", "B", "S"],
            ["A", "B", "S"]
        ],
        paytable=Paytable(
            three_kind={"A": 5, "B": 3, "S": 0}
        ),
        special_symbols={"wild": ["W"], "scatter": ["S"]},
    )

# ---------------- SIMULATION FUNCTION ----------------
def run_simulation(cfg, betmode_name="default"):
    gs = GameState(cfg, trace=True)
    force_records = []

    for i in range(NUM_SPINS):
        gs.sim = i
        # generujemy losowe symbole (dla testów używamy prostej kolejności)
        board_symbols = [reel[0] for reel in cfg.reels]
        rng = DummyRng(board_symbols)
        
        # uruchom spin
        gs.run_spin(rng, evaluator=lambda board, cfg: {"mult": 0})  # evaluator tymczasowy
        
        # Jeśli GameState ma record() i temp_wins, zbieramy custom events
        if hasattr(gs, "temp_wins") and gs.temp_wins:
            for entry in gs.temp_wins:
                force_records.append(entry)
            gs.temp_wins.clear()

    # zapisujemy do JSON
    filename = f"force_record_{betmode_name}.json"
    with open(filename, "w") as f:
        json.dump(force_records, f, indent=4)
    print(f"Symulacja zakończona. Wyniki zapisane w {filename}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Symulacja 5-bębnowa...")
    run_simulation(get_cfg_5reel(), betmode_name="5reel")
    
    print("Symulacja 3-bębnowa...")
    run_simulation(get_cfg_3reel(), betmode_name="3reel")
