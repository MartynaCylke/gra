from src.config.build_config import load_config
from src.board.board import Board
from src.utils.rng import Rng


def test_board():
    # Wczytanie konfiguracji gry
    cfg = load_config("0_0_kulki")

    # Wybór betmode (pierwszy dostępny)
    betmode = cfg.betmodes[0]

    # Utworzenie deterministycznego generatora liczb losowych
    rng = Rng(seed=42)  # ustalamy seed dla powtarzalnych wyników

    # Utworzenie planszy
    board_obj = Board(cfg=cfg, betmode=betmode, rng=rng)
    board_obj.create_board_reelstrips()  # generacja reelstrips

    # Wydrukowanie planszy
    print("Wygenerowana plansza:")
    board_obj.print_board()


if __name__ == "__main__":
    test_board()
