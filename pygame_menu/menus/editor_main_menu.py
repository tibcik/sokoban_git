"""Főmenü
"""
from __future__ import annotations

import pygame as pg

from sokoban.data import saves

from ..components.component import STICKY_DOWNLEFT, STICKY_LEFT
from ..menu import Menu
from ..components import Container, Button, Label
from .containers import TextEntryContainer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class EditorMainMenu(Menu):
    """Főmenü és játékslot választó

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        selected_player_id (id): kiválasztott játékos
        selected_button (Button): kiválasztott játékosslot gombja
    """
    def __init__(self, controller: MainController, screen: pg.Surface):
        """MainMenu

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pygame.Surface): teljes megjelenítési felület
        """
        Menu.__init__(self)

        self.controller = controller
        self.screen = screen

        self.selected_player_id = -1
        self.selected_button = None

        self.init_main_menu(None)

    def init_main_menu(self, _):
        """Főmenü betöltése
        """
        self.clear()
        self.main_container = Container(self, size=self.screen.get_size())

        b = None
        y_offset = 0
        last_player = saves.get_last_player_id()
        if last_player != -1:
            b = Button(self.main_container, "Folytatás", self.continue_game, position=(1/8,1/3), selected=True)
            y_offset = b.size[1] + 10
        b = Button(self.main_container, "Profilok", self.init_game_slot_selector_menu,
            position=(1/8,1/3+y_offset), selected=(False if b else True))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Beállítások", self.init_settings_menu, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30
        Button(self.main_container, "Kilépés", self.controller.exit, position=(1/8, 1/3+y_offset))

    def init_game_slot_selector_menu(self, _):
        """Játékosslot menü betöltése
        """
        self.clear()
        self.main_container = Container(self, size = self.screen.get_size())

        Label(self.main_container, "Játékos választás", position=(1/8,1/2-150))

        players = saves.get_players()

        Button(self.main_container, players[0] if players[0] else "Üres", self.init_player_menu, position=(1/8, 1/2-20), sticky=STICKY_DOWNLEFT, selected=True, id="0")
        Button(self.main_container, players[1] if players[1] else "Üres", self.init_player_menu, position=(1/8, 1/2), sticky=STICKY_LEFT, id="1")
        Button(self.main_container, players[2] if players[2] else "Üres", self.init_player_menu, position=(1/8, 1/2+20), id="2")

        Button(self.main_container, "Vissza", self.init_main_menu, position=(1/8, 1/2+100))

        self.add(self.main_container)

        self.selected_player_id = -1

    def init_player_menu(self, button: Button):
        """Játékos menüre váltás

        Args:
            button (Button): Kiválasztott játékos gombja
        """
        self.selected_button = button
        self.selected_player_id = int(button.id)

        if saves.get_player(self.selected_player_id):
            self.controller.init_player_menu(self.selected_player_id)
            return

        TextEntryContainer(self, "Név", self.add_player_name, position=(0,1/3), size=self.screen.get_size())

    def add_player_name(self, name: str):
        """Játékos hozzáadása

        Args:
            name (str): Játékos neve
        """
        if name is None or name == '':
            return

        saves.add_player(name, self.selected_player_id)
        self.selected_button.text = name

    def init_settings_menu(self, _):
        """NotImplemented
        """
        print("NotImplemented!")

    def continue_game(self, _):
        """Előző játék folytatása
        """
        set_name = saves.get_current_set()
        level = saves.get_current_level()

        self.controller.init_game(set_name, level)