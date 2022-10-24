""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: settings_menu.py
Verzió: 1.0.0
--------------------
pygame_menu.menus.settings_menu

Beállítások menü

Osztályok:
    SettingsMenu
"""

from __future__ import annotations

import pygame as pg

from sokoban.data import saves

from ..menu import Menu
from ..components import Container, Button, Label, Select

from sokoban import config

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class SettingsMenu(Menu):
    """Beállítások menü

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
    """
    def __init__(self, controller: MainController, screen: pg.Surface):
        """SettingsMenu

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pygame.Surface): teljes megjelenítési felület
        """
        Menu.__init__(self)

        self.controller = controller
        self.screen = screen

        self.skin_select = None
        self.fullscreen = None

        self.init_settings_menu(None)

    def init_settings_menu(self, _):
        """Beállítások menü betöltése
        """
        skins = config.get_skins()
        current_skin = saves.get_setup()

        self.clear()
        self.main_container = Container(self, "settings_back.png", size=self.screen.get_size())

        l = Label(self.main_container, "Beállítások", position=(1/8,1/6))

        y_offset = 0
        l = Label(self.main_container, "Megjelenítés", position=(1/8,1/3))
        y_offset += l.size[1] + 20
        l = Label(self.main_container, "Kinézet", position=(3/16,1/3+y_offset))
        self.skin_select = Select(self.main_container, skins, skins.index(current_skin['skin']), position=(8/16,1/3+y_offset))

        y_offset += l.size[1] + 20

        """l = Label(self.main_container, "Teljes képernyős", position=(3/16,1/3+y_offset))
        self.fullscreen = Checkbox(self.main_container, True, position=(8/16,1/3+y_offset))
        y_offset += l.size[1] + 30"""

        b = Button(self.main_container, "Mentés", self.save_settings, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Vissza", self.back, position=(1/8,1/3+y_offset))

    def save_settings(self, _):
        """Beállítások mentése
        """
        skin = self.skin_select.value
        saves.set_setup(skin, 0, 0, None)
        config.skin_name = skin

        self.back(None)

    def back(self, _):
        """Visszalépés a főmenübe
        """
        menu = self.controller.init_main_menu()
