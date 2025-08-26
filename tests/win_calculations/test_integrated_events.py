import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line

from utils.rng import DummyRng
from config.build_config import build_test_config
from symbol.symbol import Symbol


# ----------------- KONFIGURACJE -----------------

def cfg_lines_5reel():
    """Prosta konfiguracja 5-bębnowej gry liniowej"""
    return build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )


def cfg_lines_3reel():
    """Prosta konfiguracja 3-bębnowej gry liniowej"""
    return build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )


# ----------------- TESTY LINIOWE -----------------

def test_line_win_5reel():
    cfg = cfg_lines_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Board dający 3x "A"
    board = [Symbol(cfg, s) for s in ["A", "A", "A", "B", "B"]]
    gs.last_board = board
    rng = DummyRng(["A", "A", "A", "B", "B"])

    result = gs.run_spin(rng, evaluate_single_line)

    # Sprawdzenie free spins
    assert gs.free_spins == 0

    # Sprawdzenie eventu line win
    assert any(ev["type"] == "line_win" for ev in result.get("events", [])), "Brak eventu line_win"


def test_no_line_win_5reel():
    cfg = cfg_lines_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Board bez wygranej
    board = [Symbol(cfg, s) for s in ["A", "B", "K", "Q", "B"]]
    gs.last_board = board
    rng = DummyRng(["A", "B", "K", "Q", "B"])

    result = gs.run_spin(rng, evaluate_single_line)

    # Brak line_win
    assert not any(ev["type"] == "line_win" for ev in result.get("events", []))
    assert gs.free_spins == 0


# ----------------- TESTY SCATTER I FREESPIN -----------------

def test_scatter_triggers_freespin_3reel():
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Board z 3 scatterami
    board = [Symbol(cfg, s) for s in ["S", "S", "S"]]
    gs.last_board = board
    rng = DummyRng(["S", "S", "S"])

    result = gs.run_spin(rng, evaluate_single_line)

    # Sprawdzenie free spins
    assert gs.free_spins >= 10, "Free spins powinny zostać dodane"

    # Sprawdzenie scatter_event
    assert any(ev["type"] == "scatter_event" for ev in result.get("events", [])), "Brak eventu scatter_event"

    # Sprawdzenie freespin_update
    assert any(ev["type"] == "freespin_update" for ev in result.get("events", [])), "Brak eventu freespin_update"


def test_scatter_not_triggered():
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Board z mniej niż 3 scatterami
    board = [Symbol(cfg, s) for s in ["S", "A", "B"]]
    gs.last_board = board
    rng = DummyRng(["S", "A", "B"])

    result = gs.run_spin(rng, evaluate_single_line)

    # Free spins nie powinny się dodać
    assert gs.free_spins == 0

    # Scatter event nie powinien wystąpić
    assert not any(ev["type"] == "scatter_event" for ev in result.get("events", []))


# ----------------- TESTY BONUSÓW -----------------
# Jeśli Twoja gra ma inne bonusy, np. create_bonus_event, można je sprawdzić w podobny sposób

def test_bonus_event_structure():
    # Tu tylko przykład jak przetestować strukturę bonusu, jeśli byłby dodany
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # Symulacja uruchomienia bonusu
    from events.events import create_bonus_event
    create_bonus_event(gs, bonus_type="free_game", value=5)

    assert any(ev["type"] == "bonus_triggered" for ev in gs.book.get("events", [])), "Brak eventu bonus_triggered"
