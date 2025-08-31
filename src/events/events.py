from typing import Dict, Any

def create_spin_event(gs: "GameState") -> Dict[str, Any]:
    """
    Tworzy event dla rozpoczęcia spinu i dodaje go do book.
    """
    board = getattr(gs, "last_board", [])
    # Zamieniamy obiekty Symbol / listy symboli na same nazwy
    flat_board = []
    for row in board:
        if isinstance(row, list):
            flat_board.extend([s.name if hasattr(s, "name") else str(s) for s in row])
        else:
            flat_board.append(row.name if hasattr(row, "name") else str(row))

    event = {
        "index": len(gs.book.get("events", [])),
        "type": "spin_start",
        "board": flat_board,
        "spins": gs.totals.get("spins", 0),
    }
    gs.add_event(event)
    return event


def create_win_event(gs: "GameState", symbol: Any, count: int, mult: int) -> Dict[str, Any]:
    """
    Tworzy event dla wygranej symboli na linii.
    """
    event = {
        "index": len(gs.book.get("events", [])),
        "type": "line_win",
        "symbol": symbol.name if hasattr(symbol, "name") else str(symbol),
        "count": int(count),
        "mult": int(mult),
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
        "freeSpinsRemaining": int(getattr(gs, "free_spins", 0)),
        "totalWins": int(gs.totals.get("wins", 0)),
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
        "bonus_type": str(bonus_type),
        "value": int(value),
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
        "multiplier": int(multiplier),
    }
    gs.add_event(event)
    return event
