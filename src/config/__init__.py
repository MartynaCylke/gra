import sys
from ._test_config import build_test_config, TestConfig

# Alias: pozwala używać importu `src.config.test_config`
sys.modules[__name__ + ".test_config"] = sys.modules[__name__ + "._test_config"]

__all__ = ["build_test_config", "TestConfig"]
