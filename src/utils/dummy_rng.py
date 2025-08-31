from typing import List, Any, Optional
import random

class DummyRng:
    """
    Generator deterministyczny do testów.
    Zwraca wartości z listy `values` w kolejności.
    """

    def __init__(self, values: Optional[List[Any]] = None, seed: Optional[int] = None):
        self.values = values or []
        self.index = 0
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def choice(self, population: List[Any]) -> Any:
        """
        Zwraca kolejny element z values jeśli jest ustawiony,
        w przeciwnym wypadku pierwszy element population.
        """
        if self.values:
            val = self.values[self.index % len(self.values)]
            self.index += 1
            return val
        return population[0]

    def choices(self, population: List[Any], k: int) -> List[Any]:
        return [self.choice(population) for _ in range(k)]

    def choice_weighted(self, population: List[Any], weights: Optional[List[float]] = None) -> Any:
        return self.choice(population)

    def randint(self, a: int, b: int) -> int:
        """
        Zwraca kolejny element values jeśli jest int, w przeciwnym wypadku zwraca a.
        """
        if self.values:
            val = self.values[self.index % len(self.values)]
            self.index += 1
            if isinstance(val, int):
                return val
        return a
