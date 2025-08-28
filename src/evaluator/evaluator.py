"""
Evaluator odpowiedzialny za sprawdzanie wygranych na planszy.
Docelowo tutaj będzie cała logika wygrywających linii / układów.
"""

from typing import Dict, Any
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol


def evaluate_board(board, cfg: GameConfig) -> Dict[str, Any]:
    """
    Prosta funkcja oceny planszy.
    Na start zwraca tylko pustą wygraną albo testową wygraną.

    Args:
        board: lista symboli (1D albo 2D)
        cfg: konfiguracja gry (GameConfig)

    Returns:
        dict z informacją o wygranej:
            {
                "symbol": str,
                "count": int,
                "mult": int
            }
    """
    # 🔹 przykładowa, bardzo uproszczona logika:
    # sprawdzamy tylko, czy pierwszy symbol powtórzył się >= 3 razy
    flat_board = [s for row in board for s in row] if isinstance(board[0], list) else board
    if not flat_board:
        return {}

    first_symbol = flat_board[0].name
    same = sum(1 for s in flat_board if s.name == first_symbol)

    if same >= 3:
        return {
            "symbol": first_symbol,
            "count": same,
            "mult": same  # mnożnik = liczba symboli (dla testu)
        }

    return {}
