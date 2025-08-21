# src/engine.py

from config.build_config import load_config, GameConfig
from board.board import Board
from wins.lines import calculate_line_wins
from wins.wallet import Wallet

class GameEngine:
    def __init__(self, config_name: str):
        # Ładujemy konfigurację gry
        self.cfg: GameConfig = load_config(config_name)

        # Tworzymy planszę
        self.board: Board = Board(self.cfg)

        # Tworzymy portfel gracza
        self.wallet: Wallet = Wallet(cfg=self.cfg)

        # Zmienna do przechowywania wygranych z ostatniego spinu
        self.win_data = None

    def run_spin(self):
        # Tworzymy nową planszę dla spinu
        self.board = Board(self.cfg)
        print("Plansza po spinu:")
        self.board.print_board()

        # Obliczamy wygrane
        self.win_data = calculate_line_wins(self.board.board, self.cfg)

        # Wyciągamy całkowitą wygraną
        total_win = self.win_data.get("totalWin", 0)
        if total_win is None:
            total_win = 0

        # Aktualizujemy portfel
        payout = self.wallet.settle({"mult": total_win})
        print(f"Wygrana z tego spinu: {total_win}, Płatność po uwzględnieniu bet: {payout}")
        print(f"Aktualny stan portfela: {self.wallet.balance}")

        # Wyświetlamy szczegóły wygranych
        for win in self.win_data.get("wins", []):
            print(f"Symbol: {win['symbol']}, Kind: {win['kind']}, Wygrana: {win['win']}, Pozycje: {win['positions']}")

# Przykład uruchomienia
if __name__ == "__main__":
    engine = GameEngine("0_0_kulki")
    engine.run_spin()
