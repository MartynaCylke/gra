from typing import Any, Dict, Optional

class Symbol:
    def __init__(self, config: object, name: str) -> None:
        self.name: str = name
        self.special_functions: list = []
        self.special: bool = False
        self.paytable: Optional[Dict[str, Any]] = None
        self.is_paying: bool = False
        self._attributes: Dict[str, Any] = {}

        if config and getattr(config, "special_symbols", None):
            for special_property, symbols in config.special_symbols.items():
                if name in symbols:
                    setattr(self, special_property, True)
                    self.special = True

        self.assign_paying_bool(config)

    def assign_paying_bool(self, config: object) -> None:
        if not config or not getattr(config, "paytable", None):
            self.is_paying = False
            self.paytable = None
            return

        pt = config.paytable
        for table in [getattr(pt, "three_kind", None),
                      getattr(pt, "four_kind", None),
                      getattr(pt, "five_kind", None)]:
            if table and self.name in table:
                self.is_paying = True
                self.paytable = table
                return

        self.is_paying = False
        self.paytable = None

    def assign_attribute(self, attrs: Dict[str, Any]) -> None:
        self._attributes.update(attrs)

    def check_attribute(self, *keys: str) -> bool:
        return any(k in self._attributes and self._attributes[k] for k in keys)

    def get_attribute(self, key: str, default: Any = None) -> Any:
        return self._attributes.get(key, default)
