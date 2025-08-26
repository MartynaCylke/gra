import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line
from utils.rng import DummyRng
from config.build_config import build_test_config
from symbol.symbol import Symbol
from events.events import (
    create_spin_event,
    create_win_event,
    update_freespin_event,
    create_bonus_event,
    create_multiplier_event,
)


# ----------------- KONFIGURACJA TESTOWA -----------------
def cfg_5reel():
    return build_test_config(
        reels=[["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"], ["A", "B"]],
        scatter="S"
    )


# ----------------- POMOCNICZA FUNKCJA -----------------
def validate_event_fields(event: dict, required_fields: list):
    for field in required_fields:
        assert field in event, f"Brak pola '{field}' w evencie {event}"


# ----------------- TEST EVENTÓW -----------------

def test_spin_start_and_result_events():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board_symbols = ["A", "A", "B", "B", "A"]
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    # spin_start
    spin_start_events = [ev for ev in result["events"] if ev["type"] == "spin_start"]
    assert spin_start_events, "Brak eventu spin_start"
    for ev in spin_start_events:
        validate_event_fields(ev, ["index", "type", "board", "spins"])

    # spin_result
    spin_result_events = [ev for ev in result["events"] if ev["type"] == "spin_result"]
    assert spin_result_events, "Brak eventu spin_result"
    for ev in spin_result_events:
        validate_event_fields(ev, ["index", "type", "board", "win", "scatterWins"])


def test_line_win_event():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board_symbols = ["A", "A", "A", "B", "B"]  # 3x "A" → wygrana
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    line_win_events = [ev for ev in result["events"] if ev["type"] == "line_win"]
    assert line_win_events, "Brak eventu line_win"
    for ev in line_win_events:
        validate_event_fields(ev, ["index", "type", "symbol", "count", "mult"])


def test_scatter_and_freespin_events():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)
    board_symbols = ["S", "S", "S", "A", "B"]  # 3 scatter → freespins
    board = [Symbol(cfg, s) for s in board_symbols]
    gs.last_board = board
    rng = DummyRng(board_symbols)
    result = gs.run_spin(rng, evaluate_single_line)

    # scatter_event
    scatter_events = [ev for ev in result["events"] if ev["type"] == "scatter_event"]
    assert scatter_events, "Brak eventu scatter_event"
    for ev in scatter_events:
        validate_event_fields(ev, ["index", "type", "symbol", "count", "wins"])

    # freespin_update
    freespin_events = [ev for ev in result["events"] if ev["type"] == "freespin_update"]
    assert freespin_events, "Brak eventu freespin_update"
    for ev in freespin_events:
        validate_event_fields(ev, ["index", "type", "freeSpinsRemaining", "totalWins"])


def test_bonus_and_multiplier_events():
    cfg = cfg_5reel()
    gs = GameState(cfg, trace=True)
    gs.reset_book(criteria=cfg.mode)

    # bonus
    create_bonus_event(gs, bonus_type="free_game", value=5)
    bonus_events = [ev for ev in gs.book["events"] if ev["type"] == "bonus_triggered"]
    assert bonus_events, "Brak eventu bonus_triggered"
    for ev in bonus_events:
        validate_event_fields(ev, ["index", "type", "bonus_type", "value"])

    # multiplier
    create_multiplier_event(gs, multiplier=3)
    multiplier_events = [ev for ev in gs.book["events"] if ev["type"] == "multiplier_update"]
    assert multiplier_events, "Brak eventu multiplier_update"
    for ev in multiplier_events:
        validate_event_fields(ev, ["index", "type", "multiplier"])
