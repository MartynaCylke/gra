# src/config/__init__.py

import sys

# Importy z build_config
from .build_config import build_test_config, GameConfig, Paytable

# Opcjonalny import test_config, jeśli istnieje plik _test_config.py
try:
    from ._test_config import TestConfig
    # Alias dla łatwego importu
    sys.modules[__name__ + ".test_config"] = sys.modules[__name__ + "._test_config"]
except ImportError:
    TestConfig = None

# Lista eksportowanych symboli
__all__ = [
    "build_test_config",
    "GameConfig",
    "Paytable",
    "TestConfig",
]
