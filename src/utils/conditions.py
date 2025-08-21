from typing import Dict, Any, Tuple

def normalize_conditions(conditions: Dict[str, Any] | None) -> Dict[str, Any]:
    """
    Normalizuje nazwy pól w conditions, akceptując różne warianty pisowni:
      - force_wincap / forceWinCap / force_winCap
      - force_freegame / forceFreegame / force_freeGame
      - reel_weights / reels / reelWeights
      - mult_values / multiplier_values / multValues
      - scatter_triggers / scatterTriggers
    Zwraca słownik o kluczach: force_wincap, force_freegame, reel_weights, mult_values, scatter_triggers.
    """
    out = {
        "force_wincap": False,
        "force_freegame": False,
        "reel_weights": None,
        "mult_values": None,
        "scatter_triggers": None,
    }
    if not conditions:
        return out

    def get_any(keys: Tuple[str, ...], default=None):
        for k in keys:
            if k in conditions:
                return conditions[k]
        # spróbuj case-insensitive
        lower = {str(k).lower(): v for k, v in conditions.items()}
        for k in keys:
            if k.lower() in lower:
                return lower[k.lower()]
        return default

    out["force_wincap"] = bool(get_any(("force_wincap","forceWinCap","force_winCap"), False))
    out["force_freegame"] = bool(get_any(("force_freegame","forceFreegame","force_freeGame"), False))
    out["reel_weights"] = get_any(("reel_weights","reels","reelWeights"))
    out["mult_values"] = get_any(("mult_values","multiplier_values","multValues"))
    out["scatter_triggers"] = get_any(("scatter_triggers","scatterTriggers"))
    return out
