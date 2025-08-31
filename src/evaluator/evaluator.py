"""
Evaluator odpowiedzialny za sprawdzanie wygranych na planszy.
Docelowo tutaj będzie cała logika wygrywających linii / układów.
"""

from typing import Dict, Any, List, Union
from src.config.game_configs import GameConfig
from src.symbol import Symbol


BoardType = Union[List[str], List[List[str]]]

def evaluate_board(board: BoardType, cfg: GameConfig) -> Dict[str, Any]:
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
    # Spłaszczamy board do listy Symbol
    if not board:
        return {}

    flat_board: List[Symbol] = []
    if isinstance(board[0], list):
        for row in board:
            for s in row:
                if isinstance(s, Symbol):
                    flat_board.append(s)
                else:
                    flat_board.append(Symbol(cfg, s))
    else:
        for s in board:
            if isinstance(s, Symbol):
                flat_board.append(s)
            else:
                flat_board.append(Symbol(cfg, s))

    if not flat_board:
        return {}

    # Sprawdzamy pierwszy symbol
    first_symbol = flat_board[0].name
    same = sum(1 for s in flat_board if s.name == first_symbol)

    if same >= 3:
        return {
            "symbol": first_symbol,
            "count": same,
            "mult": same  # mnożnik = liczba symboli (dla testu)
        }

    return {}
