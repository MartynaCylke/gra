import csv
from pathlib import Path
from typing import Dict, List, Tuple, Iterable


def convert_range_table(pay_group: Dict[Tuple[Tuple[int, int], str], float]) -> Dict[Tuple[int, str], float]:
    """
    Zamienia pay_group:
      { ((min_kind,max_kind), "SYM"): value, ... }
    na klasyczną paytable:
      { (kind, "SYM"): value, ... } dla wszystkich kind z przedziału.
    """
    out: Dict[Tuple[int, str], float] = {}
    for (min_k, max_k), sym in pay_group.keys():
        val = pay_group[((min_k, max_k), sym)]
        for k in range(min_k, max_k + 1):
            out[(k, sym)] = val
    return out


def read_reels_csv(path: Path) -> List[List[str]]:
    """
    Czyta CSV z paskami bębnów. Oczekiwany format: każda kolumna = jeden bęben,
    każdy wiersz = kolejne zatrzymanie (stop).
    Zwraca listę kolumn: [reel_0, reel_1, ...], gdzie reel_i to lista symboli (str).
    """
    cols: List[List[str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        rdr = csv.reader(f)
        for row in rdr:
            if not row:
                continue
            # inicjalizacja kolumn
            if not cols:
                cols = [[] for _ in row]
            for i, val in enumerate(row):
                cols[i].append(val.strip())
    return cols


def validate_symbols_on_reels(
    reels: Dict[str, List[List[str]]],
    paytable_keys: Iterable[str],
    special_symbols: Dict[str, List[str]],
) -> None:
    """
    Waliduje, że każdy symbol z pasków bębnów występuje w paytable lub w special_symbols.
    Rzuca RuntimeError, gdy natrafi na nieznany symbol.
    """
    known_syms = set(paytable_keys)
    for attr_syms in special_symbols.values():
        known_syms.update(attr_syms)

    for key, reelset in reels.items():
        for idx, reel in enumerate(reelset):
            for sym in reel:
                if sym not in known_syms:
                    raise RuntimeError(f"Unknown symbol on reels ({key}, reel {idx}): {sym}")
