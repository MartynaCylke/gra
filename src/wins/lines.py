from typing import List, Dict
from src.wins.win_data import create_win_data, add_win
from src.config.build_config import GameConfig
from src.symbol.symbol import Symbol

def calculate_line_wins(board: List[List[Symbol]], cfg: GameConfig) -> Dict[str, any]:
    """
    Wylicza wygrane dla klasycznych linii (lines pays)
    """
    win_data = create_win_data()

    # cfg.paylines = lista list pozycji symboli dla każdej linii
    # przykładowo: [[(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], ...]
    for line_index, line in enumerate(cfg.paylines):
        first_symbol = board[line[0][1]][line[0][0]]  # board[row][col]
        match_count = 1
        positions = [{"reel": line[0][0], "row": line[0][1]}]

        for pos in line[1:]:
            row, col = pos[1], pos[0]
            sym = board[row][col]
            if sym.name == first_symbol.name:
                match_count += 1
                positions.append({"reel": col, "row": row})
            else:
                break

        if match_count >= cfg.min_match_count:  # minimalna liczba symboli do wygranej
            # wyliczamy wygraną dla tej linii
            base_win = cfg.paytable.get(first_symbol.name, {}).get(match_count, 0)
            add_win(win_data, first_symbol.name, match_count, base_win, positions, 
                    {"lineIndex": line_index})

    return win_data
