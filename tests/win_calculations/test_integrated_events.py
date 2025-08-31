import pytest
from state.game_state import GameState
from calculations.lines import evaluate_single_line
from utils.rng import DummyRng
from config.build_config import build_test_config
from src.symbol import Symbol
from events.events import create_bonus_event

def cfg_lines_5reel():
    return build_test_config(reels=[["A","B"]]*5, scatter="S")

def cfg_lines_3reel():
    return build_test_config(reels=[["A","B"]]*5, scatter="S")  # 5 list, żeby cols=5

def test_line_win_5reel():
    cfg = cfg_lines_5reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, s) for s in ["A","A","A","B","B"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert gs.free_spins == 0
    assert any(ev["type"]=="line_win" for ev in result.get("events", []))

def test_no_line_win_5reel():
    cfg = cfg_lines_5reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, s) for s in ["A","B","K","Q","B"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert not any(ev["type"]=="line_win" for ev in result.get("events", []))
    assert gs.free_spins == 0

def test_scatter_triggers_freespin_3reel():
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, s) for s in ["S","S","S"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert gs.free_spins >= 10
    assert any(ev["type"]=="scatter_event" for ev in result.get("events", []))
    assert any(ev["type"]=="freespin_update" for ev in result.get("events", []))

def test_scatter_not_triggered():
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    board = [Symbol(cfg, s) for s in ["S","A","B"]]
    gs.last_board = board
    rng = DummyRng([s.name for s in board])
    result = gs.run_spin(rng, evaluate_single_line)
    assert gs.free_spins == 0
    assert not any(ev["type"]=="scatter_event" for ev in result.get("events", []))

def test_bonus_event_structure():
    cfg = cfg_lines_3reel()
    gs = GameState(cfg, trace=True)
    gs.force_loader.enabled = False
    gs.reset_book(criteria=cfg.mode)

    create_bonus_event(gs, bonus_type="free_game", value=5)
    assert any(ev["type"]=="bonus_triggered" for ev in gs.book.get("events", []))
