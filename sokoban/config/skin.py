""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: skin.py
Verzió: 1.0.0
--------------------
sokoban.config.skin

Betűkészletek

Metódusok:
    set_skin_base_dir
    get_skin

Kosntansok:
    SKIN_BASE_DIR
"""
import os

SKIN_BASE_DIR = ''

def set_skin_base_dir(path: str):
    """set_skin_base_dir Kinézetek mappa beállítása

    Args:
        path (str): mappa elérési útvonala
    """
    global SKIN_BASE_DIR
    SKIN_BASE_DIR = path

def get_skins() -> list[str]:
    """get_skins Elérhető kinézetek listájának lekérdezése

    Returns:
        list[str]: elérhető kinézetek
    """
    skin_dirs = os.listdir(SKIN_BASE_DIR)

    return skin_dirs