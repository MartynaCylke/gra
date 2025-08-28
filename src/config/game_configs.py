from src.config.build_config import GameConfig, Paytable

def cfg_5reel() -> GameConfig:
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
            ["A", "B", "C", "D", "E"],
        ],
        paytable=Paytable(
            three_kind={"A": 10, "B": 5, "C": 3},
            four_kind={"A": 20, "B": 10, "C": 6},
            five_kind={"A": 50, "B": 25, "C": 15},
        ),
        special_symbols={"wild": ["W"]},
    )

def cfg_3reel() -> GameConfig:
    return GameConfig(
        id="test",
        mode="lines",
        bet=1,
        basegame_type="basegame",
        freegame_type="freegame",
        reels=[
            ["A", "B", "S"],
            ["A", "B", "S"],
            ["A", "B", "S"],
        ],
        paytable=Paytable(
            three_kind={"A": 5, "B": 3, "S": 0}
        ),
        special_symbols={"wild": ["W"], "scatter": ["S"]},
    )
