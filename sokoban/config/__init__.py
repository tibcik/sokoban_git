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
sokoban.config

Beállításokat tartalmazó csomag

Metódusok:
    set_font_base_dir
    get_font
    set_skin_base_dir
    get_skin

Konstansok:
    BASE_PATH
    DATA_PATH
    RESOURCE_PATH
    IMAGE_PATH
    SKIN_PATH
    SETS_PATH
    FONT_PATH
    DEFAULT_SET
    FESTIVAL_PATH
    FESTIVAL_EXECUTABLE
    TILE_RESOLUTION

Beállítások:
    skin_name
"""
import os

from .fonts import *
from .colors import *
from .skin import *
#from ..data import saves
#from .fonts import _set_font_base_dir

BASE_PATH = os.path.abspath(os.curdir)
DATA_PATH = BASE_PATH + "\\data\\"
RESOURCE_PATH = DATA_PATH + "res\\"
IMAGE_PATH = RESOURCE_PATH + "imgs\\"
SKIN_PATH = RESOURCE_PATH + "skins\\"
SETS_PATH = RESOURCE_PATH + "sets\\"
FONT_PATH = RESOURCE_PATH + "fonts\\"

DEFAULT_SET = "classic"

FESTIVAL_PATH = RESOURCE_PATH + "festival\\"
FESTIVAL_EXECUTABLE = FESTIVAL_PATH + "festival.exe"

set_font_base_dir(FONT_PATH)
set_skin_base_dir(SKIN_PATH)

# Alapértelmezett skin
skin_name = "kenney"
# Alapértelmezett handerő
music_volume = 10
sound_volume = 10
# Alapértelmezett felbontás
resolution = (1024,800)

TILE_RESOLUTION = (32,32)

# modul init
from ..data import saves

setup = saves.get_setup()
if setup is not None:
    skin_name = setup['skin']
    music_volume = setup['music_volume']
    sound_volume = setup['sound_volume']
    resolution = setup['res']