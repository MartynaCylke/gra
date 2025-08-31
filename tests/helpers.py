# tests/helpers.py

class DummyRng:
    def __init__(self, values):
        self.values = values
        self.index = 0
    def next(self):
        val = self.values[self.index % len(self.values)]
        self.index += 1
        return val

def build_test_config(scatter="S"):
    class DummyCfg:
        def __init__(self):
            self.grid_width = 5
            self.grid_height = 3
            self.scatter_symbol = scatter
            self.reels = 5
            self.betmodes = [1]
            self.special_symbols = {"wild": ["W"]}
            self.paytable = None
    return DummyCfg()

cfg_5reel = build_test_config()
