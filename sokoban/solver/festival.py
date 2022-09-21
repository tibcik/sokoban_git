from __future__ import annotations

import os

from sokoban.data import loader
from sokoban import config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sokoban import Space

def clear():
    resources = ("tmp.sok", "solutions.sok", "times.txt")

    for res in resources:
        path_str = f"{config.FESTIVAL_PATH}{res}"
        if os.path.isfile(path_str):
            os.remove(path_str)

def space_to_level_str(space: Space):
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

def save_level(layout):
    with open(f"{config.FESTIVAL_PATH}tmp.sok", "wt") as f:
        for line in layout:
            f.write(line + "\n")

def get_solution():
    with open(f"{config.FESTIVAL_PATH}solutions.sok") as f:
        line = f.readline()
        while line:
            line = line.strip()
            if line == "Solution":
                return f.readline().strip()
            line = f.readline()

    return ""