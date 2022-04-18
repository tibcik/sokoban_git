from .fonts import *
from .colors import *
from ..data import saves

# Alapértelmezett skin
skin_name = "default"
# Alapértelmezett handerő
music_volume = 10
sound_volume = 10
# Alapértelmezett felbontás
resolution = (1024,800)

TILE_RESOLUTION = (32,32)

# modul init
setup = saves.get_setup()
if setup is not None:
    skin_name = setup['skin']
    music_volume = setup['music_volume']
    sound_volume = setup['sound_volume']
    resolution = setup['res']