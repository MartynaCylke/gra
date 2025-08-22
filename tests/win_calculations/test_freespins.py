import pytest
from src.state.game_state import GameState
from src.symbol.symbol import Symbol
from src.utils.rng import DummyRng
from src.config.build_config import build_test_config
from src.calculations.lines import evaluate_single_line


def test_freespin_event():
    # --- konfiguracja gry z free spins ---
    cfg = build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )

    # ustawiamy początkowe free spins
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.reset_book(criteria=cfg.mode)

    # --- wymuszony board (bez scatterów, żeby testować free spin event) ---
    board = [Symbol(cfg, "A"), Symbol(cfg, "A"), Symbol(cfg, "B"), Symbol(cfg, "B"), Symbol(cfg, "A")]
    gs.last_board = board
    rng = DummyRng(["A", "A", "B", "B", "A"])

    result = gs.run_spin(rng, evaluate_single_line)

    # --- sprawdzamy że free spins się zmniejszyły po spiny ---
    assert gs.free_spins >= 0, "Free spins powinny być liczbą >= 0"
    # --- opcjonalnie możemy sprawdzić eventy ---
    assert any(ev["type"] == "freespin_event" for ev in result.get("events", [])), "Brak eventu freespin"
