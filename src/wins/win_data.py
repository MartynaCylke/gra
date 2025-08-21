from typing import List, Dict, Any

def create_win_data() -> Dict[str, Any]:
    """
    Tworzy podstawową strukturę win_data dla spinów.
    """
    return {
        "totalWin": 0.0,  # całkowita wygrana w spinie
        "wins": []         # lista pojedynczych wygranych
    }


def add_win(win_data: Dict[str, Any], symbol: str, kind: int, win_amount: float,
            positions: List[Dict[str, int]], meta: Dict[str, Any] = None) -> None:
    """
    Dodaje pojedynczą wygraną do struktury win_data.
    """
    if meta is None:
        meta = {}

    win_entry = {
        "symbol": symbol,       # symbol wygrywający
        "kind": kind,           # liczba symboli w linii / cluster
        "win": win_amount,      # kwota wygranej
        "positions": positions, # lista pozycji: {"reel": int, "row": int}
        "meta": meta            # dodatkowe informacje
    }

    win_data["wins"].append(win_entry)
    win_data["totalWin"] += win_amount
