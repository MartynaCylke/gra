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
