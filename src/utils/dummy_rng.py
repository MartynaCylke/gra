class DummyRng:
    def __init__(self, values):
        self.values = values
        self.index = 0

    def choice(self, _):
        val = self.values[self.index % len(self.values)]
        self.index += 1
        return val

    def choices(self, population, k):
        return [self.choice(population) for _ in range(k)]
