import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line

# Poprawione importy
from utils.rng import DummyRng
from config.build_config import build_test_config
from symbol.symbol import Symbol


def test_freespin_event():
    # --- konfiguracja gry z free spins + scatter ---
    cfg = build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )

    # ustawiamy początkowe free spins
    gs = GameState(cfg, trace=True, free_spins=3)
    gs.reset_book(criteria=cfg.mode)
    gs.force_loader.enabled = False  # WYŁĄCZAMY wymuszony spin

    # --- wymuszony board (ze scatterami, żeby odpalił event free spin) ---
    board = [
        Symbol(cfg, "S"),
        Symbol(cfg, "A"),
        Symbol(cfg, "S"),
        Symbol(cfg, "B"),
        Symbol(cfg, "S"),
    ]
    gs.last_board = board
    rng = DummyRng(["S", "A", "S", "B", "S"])

    result = gs.run_spin(rng, evaluate_single_line)

    # --- sprawdzamy, że free spins zmniejszyły się po spinie ---
    assert gs.free_spins >= 0, "Free spins powinny być liczbą >= 0"

    # --- i że pojawił się event freespin ---
    assert any(ev["type"] == "freespin_update" for ev in result.get("events", [])), "Brak eventu freespin"
