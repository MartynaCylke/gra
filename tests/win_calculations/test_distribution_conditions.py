import pytest
from src.config.build_config import GameConfig, BetMode, Distribution


def test_distribution_conditions_normalization_basic():
    dist = Distribution(
        criteria="basegame",
        quota=1.0,
        conditions={"forceWinCap": True, "multiplier_values": [2, 3]}
    )
    bm = BetMode(name="base", cost=1.0, distributions=[dist])
    conds = bm.get_distribution_conditions()

    assert isinstance(conds, list)
    assert len(conds) == 1
    c = conds[0]

    # powinno się znormalizować do standardowych nazw
    assert c["force_wincap"] is True
    assert c["mult_values"] == [2, 3]
    assert "force_freegame" in c
    assert "reel_weights" in c
    assert "scatter_triggers" in c


def test_distribution_conditions_empty():
    bm = BetMode(name="base", cost=1.0, distributions=[Distribution("basegame", 1.0)])
    conds = bm.get_distribution_conditions()
    assert conds[0]["force_wincap"] is False
    assert conds[0]["force_freegame"] is False


def test_distribution_conditions_various_keys():
    dist = Distribution(
        criteria="freegame",
        quota=0.5,
        conditions={
            "force_freeGame": True,
            "reels": {"R1": [1, 2, 3]},
            "multValues": [10],
            "scatterTriggers": {"SCAT": 3},
        },
    )
    bm = BetMode(name="bonus", cost=2.0, distributions=[dist])
    conds = bm.get_distribution_conditions()
    c = conds[0]

    assert c["force_freegame"] is True
    assert c["reel_weights"] == {"R1": [1, 2, 3]}
    assert c["mult_values"] == [10]
    assert c["scatter_triggers"] == {"SCAT": 3}
