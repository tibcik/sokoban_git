""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: festival.py
Verzió: 1.0.0
--------------------
sokoban.solver.festival

Sokoban festival solvernek előkészítő metódusok

Metódusok:
    clear
    space_to_level_str
    save_level
    get_solution
"""
from __future__ import annotations

import os

from sokoban.data import loader
from sokoban import config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sokoban import Space

def clear():
    """clear festival solver által létrehozott fájlok törlése
    """
    resources = ("tmp.sok", "solutions.sok", "times.txt")

    for res in resources:
        path_str = f"{config.FESTIVAL_PATH}{res}"
        if os.path.isfile(path_str):
            os.remove(path_str)

def space_to_level_str(space: Space) -> str:
    """space_to_level_str Játéktér átalakítása karakterlánccá

    Args:
        space (Space): Játéktér objektum

    Returns:
        str: Játéktér karakterlánc reprezentációja
    """
    layout = ['']
    
    for elem in space:
        if elem is None:
            layout.append('')
        elif elem & loader.SOKOBAN_GOAL:
            if elem & loader.SOKOBAN_BOX:
                layout[-1] += '*'
            elif elem & loader.SOKOBAN_PLAYER:
                layout[-1] += '+'
            else:
                layout[-1] += '.'
        elif elem & loader.SOKOBAN_BOX:
            layout[-1] += '$'
        elif elem & loader.SOKOBAN_PLAYER:
            layout[-1] += '@'
        elif elem & loader.SOKOBAN_WALL:
            layout[-1] += '#'
        else:
            layout[-1] += ' '

    return layout

def save_level(layout: str):
    """save_level Játéktér elmentése a festival solvernek

    Args:
        layout (str): Játéktér karakterlánc reprezentációja
    """
    with open(f"{config.FESTIVAL_PATH}tmp.sok", "wt") as f:
        for line in layout:
            f.write(line + "\n")

def get_solution() -> str:
    """get_solution Megoldás keolvasása a festival által készített fájlból

    Returns:
        str: megoldás
    """
    with open(f"{config.FESTIVAL_PATH}solutions.sok") as f:
        line = f.readline()
        while line:
            line = line.strip()
            if line == "Solution":
                return f.readline().strip()
            line = f.readline()

    return ""