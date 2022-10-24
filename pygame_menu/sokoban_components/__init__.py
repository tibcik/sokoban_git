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
pygame_menu.sokoban_componenets

A játékhoz készített külön komponensek.

Osztályok:
    SLevel
    SSet
"""
from .slevel import SLevel
from .sset import SSet

__all__ = ["SLevel", "SSet"]