from typing import List, Any


class DummyRng:
    """
    Generator deterministyczny do testów. Zwraca wartości podane w `values` w kolejności.
    """

    def __init__(self, values: List[Any]):
        self.values = values
        self.index = 0

    def choice(self, population: List[Any]) -> Any:
        """
        Zwraca kolejny element z listy values ignorując population.
        """
        val = self.values[self.index % len(self.values)]
        self.index += 1
        return val

    def choices(self, population: List[Any], k: int) -> List[Any]:
        """
        Zwraca listę k elementów z values, w kolejności.
        """
        return [self.choice(population) for _ in range(k)]

    def choice_weighted(self, population: List[Any], weights: List[float] = None) -> Any:
        """
        Ignoruje weights, zwraca kolejny element z values. Kompatybilne z GameState.make_board.
        """
        return self.choice(population)
