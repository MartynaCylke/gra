from typing import List, Dict, Any, Optional
from src.config.build_config import GameConfig


def _wild_set(cfg: GameConfig) -> set:
    """
    Zwraca zbiór symboli Wild z configu (domyślnie {'W'}).
    """
    if cfg.special_symbols and isinstance(cfg.special_symbols.get("wild"), list):
        return set(cfg.special_symbols["wild"])
    return {"W"}


def _best_symbol_for_all_wilds(cfg: GameConfig) -> str:
    """
    Jeśli cała linia to Wildy, wybierz symbol o najwyższej wypłacie (na podstawie 3oak),
    żeby policzyć maksymalny sensowny wynik.
    """
    if cfg.paytable and cfg.paytable.three_kind:
        # wybierz symbol o największym mnożniku 3oak
        return max(cfg.paytable.three_kind.items(), key=lambda kv: kv[1])[0]
    return "A"


def _read_extra_paytable(cfg: GameConfig, key: str) -> Optional[Dict[str, int]]:
    """
    Opcjonalnie odczytaj dodatkowe mapy wypłat (np. 4oak/5oak), jeśli kiedyś dodasz je do GameConfig
    jako atrybuty: cfg.paytable_4oak, cfg.paytable_5oak. Gdy brak – zwróć None.
    """
    try:
        return getattr(cfg, key)
    except Exception:
        return None


def evaluate_lines_5reel(board: List[str], cfg: GameConfig) -> Dict[str, Any]:
    """
    Evaluator dla pojedynczej linii 5-bębnowej (od lewej, Wild zastępuje).
    Wypłaty: 3/4/5-of-a-kind. Jeśli nie masz 4oak/5oak w configu, stosuje bezpieczny fallback:
      4oak ≈ 2 * (3oak), 5oak ≈ 4 * (3oak)

    Zwraca dict np. {"line": 0, "symbol": "A", "count": 4, "mult": 10} lub {} gdy brak wygranej.
    """
    # Board powinien mieć >= 5 symboli
    if not isinstance(board, list) or len(board) < 5:
        return {}

    wilds = _wild_set(cfg)

    # Wyznacz symbol celu: pierwszy nie-wild z lewej
    target = None
    for s in board:
        if s not in wilds:
            target = s
            break
    if target is None:
        # cała linia z Wildów
        target = _best_symbol_for_all_wilds(cfg)

    # Policz ile kolejnych symboli od lewej pasuje (target lub Wild)
    n = 0
    for s in board:
        if s == target or s in wilds:
            n += 1
        else:
            break

    if n < 3 or not cfg.paytable:
        return {}

    # Podstawowa tabela 3oak
    three_map = cfg.paytable.three_kind or {}

    # Opcjonalne tabele 4oak/5oak (jeśli kiedyś je dodasz do GameConfig)
    four_map = _read_extra_paytable(cfg, "paytable_4oak")
    five_map = _read_extra_paytable(cfg, "paytable_5oak")

    mult = 0
    if n >= 5:
        if five_map and target in five_map:
            mult = int(five_map[target])
        else:
            base = int(three_map.get(target, 0))
            mult = 4 * base  # fallback, gdy brak 5oak
    elif n == 4:
        if four_map and target in four_map:
            mult = int(four_map[target])
        else:
            base = int(three_map.get(target, 0))
            mult = 2 * base  # fallback, gdy brak 4oak
    else:  # n == 3
        mult = int(three_map.get(target, 0))

    if mult <= 0:
        return {}

    return {"line": 0, "symbol": target, "count": n, "mult": mult}
