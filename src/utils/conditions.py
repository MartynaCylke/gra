from typing import Dict, Any, Tuple, Optional
import random

def normalize_conditions(conditions: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Normalizuje nazwy pól w conditions, akceptując różne warianty pisowni.
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
        # Najpierw bezpośrednio
        for k in keys:
            if k in conditions:
                return conditions[k]
        # Potem case-insensitive
        lower = {str(k).lower(): v for k, v in conditions.items()}
        for k in keys:
            if k.lower() in lower:
                return lower[k.lower()]
        return default

    out["force_wincap"] = bool(get_any(("force_wincap", "forceWinCap", "force_winCap"), False))
    out["force_freegame"] = bool(get_any(("force_freegame", "forceFreegame", "force_freeGame"), False))
    out["reel_weights"] = get_any(("reel_weights", "reels", "reelWeights"))
    out["mult_values"] = get_any(("mult_values", "multiplier_values", "multValues"))
    out["scatter_triggers"] = get_any(("scatter_triggers", "scatterTriggers"))
    return out


# -------------------- DISTRIBUTION CONDITION --------------------

class DistributionCondition:
    def __init__(
        self,
        criteria: str,
        quota: float,
        conditions: Dict[str, Any],
        win_criteria: Optional[float] = None
    ):
        """
        Reprezentuje jeden warunek wygranej w BetMode.
        """
        self.criteria = criteria
        self.quota = quota
        self.conditions = normalize_conditions(conditions)
        self.win_criteria = win_criteria


class DistributionSet:
    def __init__(self):
        """
        Manager dla wielu DistributionCondition.
        """
        self.conditions: list[DistributionCondition] = []

    def add_condition(self, condition: DistributionCondition):
        """
        Dodaje nowy warunek do zestawu.
        """
        self.conditions.append(condition)

    def get_distribution_conditions(self) -> Dict[str, Any]:
        """
        Zwraca losowy warunek zgodnie z quota.
        """
        if not self.conditions:
            return normalize_conditions(None)

        # Normalizacja kwot (quota)
        total_quota = sum(c.quota for c in self.conditions)
        probabilities = [c.quota / total_quota for c in self.conditions]

        selected_condition = random.choices(self.conditions, weights=probabilities, k=1)[0]
        result = selected_condition.conditions.copy()
        if selected_condition.win_criteria is not None:
            result["win_criteria"] = selected_condition.win_criteria
        return result
