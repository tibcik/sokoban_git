from turtle import position
import pygame as pg
from pygame_menu.components.component import STICKY_DOWNLEFT, STICKY_LEFT


from ..menu import Menu
from ..components import Container, Button, Label, TextEntry
from .containers import TextEntryContainer, SelectContainer, LevelSelectorContainer

import config.saves as saves

class PlayerMenu(Menu):
    def __init__(self, controller, screen, selected_player_id):
        Menu.__init__(self)

        assert saves.get_player(selected_player_id) is not None, (f"Hibás player id."
            f"Várt 0-2 intervallumban és létező player, kapott {selected_player_id}")

        self.controller = controller
        self.screen = screen

        self.selected_player_id = selected_player_id
        saves.set_last_player(self.selected_player_id)

        self.init_player_menu(None)

    def init_player_menu(self, _):
        self.clear()
        self.main_container = Container(self, size=self.screen.get_size())

        player_name = saves.get_player(self.selected_player_id)

        self.player_label = Label(self.main_container, f"Játékos: {player_name}", position=(1/8,1/4))

        y_offset = 0
        b = Button(self.main_container, "Folytatás", None, True, position=(1/8,1/3))
        y_offset += b.size[1] + 20
        b = Button(self.main_container, "Szint választása", self.init_select_level, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Készlet választása", None, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30
        b = Button(self.main_container, "Játékos átnevezése", self.init_rename_player, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Játékos törlése", self.init_delete_player, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30
        b = Button(self.main_container, "Vissza", self.back, position=(1/8,1/3+y_offset))

    def continue_game(self, _):
        print("NotImplemented!")

    def init_select_level(self, _):
        set_name = saves.get_current_set(self.selected_player_id)
        LevelSelectorContainer(self, None, set_name, self.selected_player_id, size=self.screen.get_size())

    def init_select_set(self, _):
        print("NotImplemented!")

    def init_rename_player(self, _):
        name = saves.get_player(self.selected_player_id)
        TextEntryContainer(self, "Név", self.rename_player, name, size=self.screen.get_size())

    def rename_player(self, name):
        if name is None or name == "":
            return

        saves.add_player(name, self.selected_player_id)
        self.player_label.text = f"Játékos: {name}"

    def init_delete_player(self, _):
        SelectContainer(self, "Biztos törlöd a játékost?", self.delete_player, size=self.screen.get_size())

    def delete_player(self, delete):
        if delete:
            saves.remove_player(self.selected_player_id)
            self.back(None)

    def back(self, _):
        menu = self.controller.init_main_menu()
        menu.init_game_slot_selector_menu(None)