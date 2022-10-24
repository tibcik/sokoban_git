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
pygame_menu.menus

A játékhoz készített menük.

Osztályok:
    MainMenu
    PlayerMenu
    GameMenu
    SettingsMenu
    EditorMainMenu
"""

from .main_menu import MainMenu
from .player_menu import PlayerMenu
from .game_menu import GameMenu
from .settings_menu import SettingsMenu
from .editor_main_menu import EditorMainMenu

__all__ = ["MainMenu", "PlayerMenu", "GameMenu", "SettingsMenu", "EditorMainMenu"]