import os

from .fonts import *
from .colors import *
#from ..data import saves
#from .fonts import _set_font_base_dir

BASE_PATH = os.path.abspath(os.curdir)
DATA_PATH = BASE_PATH + "\\data\\"
RESOURCE_PATH = DATA_PATH + "res\\"
SKIN_PATH = RESOURCE_PATH + "skins\\"
SETS_PATH = RESOURCE_PATH + "sets\\"
FONT_PATH = RESOURCE_PATH + "fonts\\"

FESTIVAL_PATH = RESOURCE_PATH + "festival\\"
FESTIVAL_EXECUTABLE = FESTIVAL_PATH + "festival.exe"

set_font_base_dir(FONT_PATH)

# Alapértelmezett skin
skin_name = "kenney"
# Alapértelmezett hangerő
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