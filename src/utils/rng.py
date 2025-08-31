# src/utils/rng.py
import random
from typing import Optional, List

class Rng:
    """Klasa generatora losowego, obsługuje seed opcjonalnie."""
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed
        self._random = random.Random(seed)

    def randint(self, a: int, b: int) -> int:
        return self._random.randint(a, b)

    def choice(self, seq: List):
        return self._random.choice(seq)

    def shuffle(self, seq: List):
        self._random.shuffle(seq)

class DummyRng(Rng):
    """Dummy RNG używany w testach. Zwraca zawsze pierwsze elementy sekwencji."""
    def __init__(self, seed: Optional[int] = None):
        # ignorujemy seed, ale pozwalamy na jego przekazanie
        pass

    def randint(self, a: int, b: int) -> int:
        return a  # zawsze zwracamy najniższą wartość

    def choice(self, seq: List):
        return seq[0] if seq else None

    def shuffle(self, seq: List):
        # nic nie robimy, kolejność pozostaje taka sama
        pass
