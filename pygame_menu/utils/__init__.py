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
pygame_menu.utils

Menürendszerhesz tartozó kisegítő metódusok és osztályok

Osztályok:
    EventHandler

Metódusok:
    image_loader

Konstansok:
    HORIZONTAL
    VERTICAL
"""

from .event_handler import EventHandler
from sokoban import config
import pygame as pg

HORIZONTAL = 0
VERTICAL = 1

__all__ = ["EventHandler", "HORIZONTAL", "VERTICAL"]

def image_loader(img_name: str) -> pg.Surface | None:
    """image_loader Képbetöltő metódus

    Args:
        img_name (str): képfájl neve

    Returns:
        pg.Surface | None: kép
    """
    try:
        img = pg.image.load(f"{config.SKIN_PATH}{config.skin_name}/{img_name}").convert_alpha()
    except:
        try:
            img = pg.image.load(f"{config.IMAGE_PATH}{img_name}").convert_alpha()
        except:
            return None

    return img