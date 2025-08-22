import random
from typing import Sequence, Optional, List, Any

class Rng:
    def __init__(self, seed: int):
        self._rng = random.Random(seed)

    def choice(self, seq: Sequence[Any]):
        return self._rng.choice(seq)

    def choice_weighted(self, seq: Sequence[Any], weights: Optional[Sequence[float]] = None):
        # Zwraca 1 element z seq wg wag; gdy weights=None -> równomiernie
        if weights is None:
            return self.choice(seq)
        return self._rng.choices(seq, weights=weights, k=1)[0]

    def randint(self, a, b):
        return self._rng.randint(a, b)

    def random(self):
        return self._rng.random()

    def state(self):
        return self._rng.getstate()

    def set_state(self, s):
        self._rng.setstate(s)


# --- Dodajemy DummyRng do testów ---
class DummyRng:
    """RNG zwracający zawsze kolejne wartości z listy podanej w initializerze"""
    def __init__(self, values: List[Any]):
        self.values = list(values)
        self.index = 0

    def choice(self, _):
        # ignorujemy argument (np. reel), zwracamy po kolei z listy values
        if self.index >= len(self.values):
            self.index = 0
        val = self.values[self.index]
        self.index += 1
        return val

    def choice_weighted(self, seq: Sequence[Any], weights: Optional[Sequence[float]] = None):
        # ignorujemy weights, po prostu zwracamy po kolei
        return self.choice(seq)
