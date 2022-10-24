""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: fonts.py
Verzió: 1.0.0
--------------------
sokoban.config.fonts

Betűkészletek

Metódusok:
    set_font_base_dir
    get_font

Kosntansok:
    SMALLEST_FONT_SIZE
    SMALL_FONT_SIZE
    DEFAULT_FONT_SIZE
    BIG_FONT_SIZE
    BIGGEST_FONT_SIZE
    DEFAULT_FONT
    BUTTON_FONT
    LABEL_FONT
    TEXTENTRY_FONT
    SELECT_FONT
    FONT_BASE_DIR
"""
import pygame as pg

SMALLEST_FONT_SIZE = 12
SMALL_FONT_SIZE = 18
DEFAULT_FONT_SIZE = 24
BIG_FONT_SIZE = 30
BIGGEST_FONT_SIZE = 36

DEFAULT_FONT = 'karma.suture-regular.otf'
BUTTON_FONT = 'karma.suture-regular.otf'
LABEL_FONT = 'karma.suture-regular.otf'
TEXTENTRY_FONT = 'karma.suture-regular.otf'
SELECT_FONT = 'karma.suture-regular.otf'

FONT_BASE_DIR = ''

fonts = {}

def set_font_base_dir(path: str):
    """set_font_base_dir Betűkészletek mappa beállítása

    Args:
        path (str): mappa elérési útvonala
    """
    global FONT_BASE_DIR
    FONT_BASE_DIR = path

def get_font(font_name: str = DEFAULT_FONT, font_size: int = DEFAULT_FONT_SIZE) -> pg.font.Font:
    """Pygame font

    Args:
        font_name (str, optional): betűkészlet neve(elérési útja). Defaults to DEFAULT_FONT.
        font_size (int, optional): betűkészlet mérete. Defaults to DEFAULT_FONT_SIZE.

    Returns:
        pygame.font.Font: Kiválasztott betűkészlet
    """
    global FONT_BASE_DIR, fonts

    f_name = f"{font_name}_{font_size}"
    
    if f_name not in fonts:
        fonts[f_name] = pg.font.Font(f"{FONT_BASE_DIR}{font_name}", font_size)

    return fonts[f_name]