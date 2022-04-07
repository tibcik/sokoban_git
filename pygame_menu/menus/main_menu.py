import pygame as pg
from pygame_menu.components.component import STICKY_DOWNLEFT, STICKY_LEFT

from utils.pair import Pair

from ..menu import Menu
from ..components import Container, Button, Label, TextEntry
from .containers import TextEntryContainer

import config.saves as saves

class MainMenu(Menu):
    def __init__(self, controller, screen):
        Menu.__init__(self)

        self.controller = controller
        self.screen = screen

        self.selected_player_id = -1
        self.selected_button = None

        self.init_main_menu(None)

    def init_main_menu(self, _):
        self.clear()
        self.main_container = Container(self, size=self.screen.get_size())

        y_offset = 0
        last_player = saves.get_last_player_id()
        if last_player != -1:
            b = Button(self.main_container, "Folytatás", self.continue_game, position=(1/8,1/3))
            y_offset = b.size[1] + 10
        b = Button(self.main_container, "Új játék", self.init_game_slot_selector_menu,
            position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        Button(self.main_container, "Kilépés", self.controller.exit, position=(1/8, 1/3+y_offset))

    def init_game_slot_selector_menu(self, _):
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

    def init_player_menu(self, button):
        self.selected_button = button
        self.selected_player_id = int(button.id)

        if saves.get_player(self.selected_player_id):
            self.controller.init_player_menu(self.selected_player_id)
            return

        TextEntryContainer(self, "Név", self.add_player_name, position=(0,1/3), size=self.screen.get_size())

    def add_player_name(self, name):
        if name is None or name == '':
            return

        saves.add_player(name, self.selected_player_id)
        self.selected_button.text = name

    def continue_game(self, button):
        print("NotImplemented!")