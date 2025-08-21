from src.config.build_config import load_config
from src.board.board import Board

def test_board():
    # Wczytanie konfiguracji gry
    cfg = load_config("0_0_kulki")

    # Utworzenie planszy
    board_obj = Board(cfg)

    # Wydrukowanie planszy
    print("Wygenerowana plansza:")
    board_obj.print_board()

if __name__ == "__main__":
    test_board()
