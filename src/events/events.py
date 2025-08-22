from typing import Dict, Any

def create_spin_event(gs: "GameState") -> Dict[str, Any]:
    """
    Tworzy event dla rozpoczęcia spinu i dodaje go do book.
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "spin_start",
        "board": getattr(gs, "last_board", []),
        "spins": gs.totals.get("spins", 0),
    }
    gs.add_event(event)
    return event


def create_win_event(gs: "GameState", symbol: str, count: int, mult: int) -> Dict[str, Any]:
    """
    Tworzy event dla wygranej symboli na linii.
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "line_win",
        "symbol": symbol,
        "count": count,
        "mult": mult,
    }
    gs.add_event(event)
    return event


def update_freespin_event(gs: "GameState") -> Dict[str, Any]:
    """
    Tworzy event dla aktualizacji freespinów i dodaje do book.
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "freespin_update",
        "freeSpinsRemaining": getattr(gs, "free_spins", 0),
        "totalWins": gs.totals.get("wins", 0),
    }
    gs.add_event(event)
    return event


def create_bonus_event(gs: "GameState", bonus_type: str, value: int) -> Dict[str, Any]:
    """
    Tworzy event uruchomienia bonusu (np. freespiny).
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "bonus_triggered",
        "bonus_type": bonus_type,
        "value": value,
    }
    gs.add_event(event)
    return event


def create_multiplier_event(gs: "GameState", multiplier: int) -> Dict[str, Any]:
    """
    Tworzy event aktualizacji mnożnika wygranej.
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "multiplier_update",
        "multiplier": multiplier,
    }
    gs.add_event(event)
    return event
