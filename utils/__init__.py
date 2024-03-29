""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: __init__.py
Verzió: 1.0.0
--------------------
utils

Általános kiegészítő osztályok és függvények"""
from __future__ import annotations

from .pair import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

def between(val: int | float, minv: int | float, maxv: int | float) -> bool:
    """Érték vizsgálata, hogy egy tartományba esik-e.
    
    Args:
        val: vizsgált érték
        minv: minimum érték
        maxv: maximum érték"""
    if minv > maxv:
        minv, maxv = maxv, minv
    return minv < val and maxv > val

def betweens(val: int | float, minv: int | float, maxv: int | float) -> int | float:
    """Érték vizsgálata, hogy egy tartományba esik-e és beállítás
    
    Args:
        val: vizsgált érték
        minv: minimum érték
        maxv: maximum érték
        
    Return:
        Ha a tartományba esik akkor a kapott érték, ha nem akkor a szélsőérték
        ahol a tartományból kilépett."""
    if minv > maxv:
        minv, maxv = maxv, minv
    return minv if val < minv else maxv if val > maxv else val

__all__ = ["Pair", "between", "betweens"]