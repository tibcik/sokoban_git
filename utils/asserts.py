"""Előre megírt assertek"""
from __future__ import annotations

def type_assert(v_name: str, v: any, t: any):
    """Típus ellenőrzés

    Args:
        v_name (str): változó neve
        v (any): változó
        t (any): típus

    Returns:
        str: hiba szövege
    """
    assert type(v) == t, f"Várt típus a '{v_name}' változónak :{type(t)}; kapott típus: {type(v)}"

def list_len_assert(v_name: str, v: any, min_l: int = 0, max_l: int | None = None):
    """Lista hosszának ellenőrzése

    Args:
        v_name (str): változó neve
        v (any): változó
        min_l (int): minimális méret
        max_l (int | None): maximális méret, ha None akkor végtelen
    """

    assert hasattr(v, "__len__") and hasattr(v, "__getitem__"), (f"Várt indexelhető objektum a "
        f"'{v_name}' változóban; kapott típus: {type(v)}")

    if max_l is None:
        _max_l = len(v)
    assert len(v) >= min_l and len(v) <= _max_l, (f"Várt legalább {min_l} elem, " +
        ("" if max_l is None else f"legfeljebb {max_l} elem,") +
        f" '{v_name}' változóban; kapott objektum elemszáma: {len(v)}")