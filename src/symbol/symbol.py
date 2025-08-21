from typing import Any, Dict, Optional


class Symbol:
    def __init__(self, config: object, name: str) -> None:
        self.name: str = name
        self.special_functions: list = []
        self.special: bool = False
        self.paytable: Optional[Dict[str, Any]] = None
        self.is_paying: bool = False
        self._attributes: Dict[str, Any] = {}

        # --- sprawdzanie special_symbols z configu ---
        is_special = False
        if config and getattr(config, "special_symbols", None):
            for special_property in config.special_symbols.keys():
                if name in config.special_symbols[special_property]:
                    setattr(self, special_property, True)
                    is_special = True

        if is_special:
            self.special = True

        # --- przypisanie płatności ---
        self.assign_paying_bool(config)

    # --- przypisanie flagi is_paying oraz paytable ---
    def assign_paying_bool(self, config: object) -> None:
        if not config or not getattr(config, "paytable", None):
            self.is_paying = False
            self.paytable = None
            return

        pt = config.paytable
        if pt and getattr(pt, "three_kind", None):
            if self.name in pt.three_kind:
                self.is_paying = True
                self.paytable = pt.three_kind
                return
        # jeśli symbol nie płaci
        self.is_paying = False
        self.paytable = None

    # --- atrybuty dynamiczne (np. multiplier, prize, itd.) ---
    def assign_attribute(self, attrs: Dict[str, Any]) -> None:
        """Dodaje/aktualizuje atrybuty symbolu"""
        self._attributes.update(attrs)

    def check_attribute(self, *keys: str) -> bool:
        """
        Zwraca True jeśli symbol ma atrybut (i jest != False).
        Można sprawdzać kilka kluczy naraz.
        """
        return any(k in self._attributes and self._attributes[k] for k in keys)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)
