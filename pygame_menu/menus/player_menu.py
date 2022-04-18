"""Főmenü
"""
from __future__ import annotations

import pygame as pg

from sokoban.data import saves

from ..components.component import STICKY_DOWNLEFT, STICKY_LEFT
from ..menu import Menu
from ..components import Container, Button, Label
from .containers import SetSelectorContainer, TextEntryContainer, SelectContainer, LevelSelectorContainer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class PlayerMenu(Menu):
    """Játékos menü

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        selected_player_id (id): kiválasztott játékos
    """
    def __init__(self, controller: MainController, screen: pg.Surface, selected_player_id: int):
        """MainMenu

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pygame.Surface): teljes megjelenítési felület
            selected_player_id (id): kiválasztott játékos
        """
        Menu.__init__(self)

        assert saves.get_player(selected_player_id) is not None, (f"Hibás player id."
            f"Várt 0-2 intervallumban és létező player, kapott {selected_player_id}")

        self.controller = controller
        self.screen = screen

        self.selected_player_id = selected_player_id
        saves.set_last_player(self.selected_player_id)

        self.init_player_menu(None)

    def init_player_menu(self, _):
        """Játékos menü betöltése
        """
        self.clear()
        self.main_container = Container(self, size=self.screen.get_size())

        player_name = saves.get_player(self.selected_player_id)

        self.player_label = Label(self.main_container, f"Játékos: {player_name}", position=(1/8,1/4))

        y_offset = 0
        b = Button(self.main_container, "Folytatás", self.continue_game, True, position=(1/8,1/3))
        y_offset += b.size[1] + 20
        b = Button(self.main_container, "Szint választása", self.init_select_level, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Készlet választása", self.init_select_set, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30
        b = Button(self.main_container, "Játékos átnevezése", self.init_rename_player, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Játékos törlése", self.init_delete_player, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30
        b = Button(self.main_container, "Vissza", self.back, position=(1/8,1/3+y_offset))

    def continue_game(self, _):
        """Játék folytatása
        """
        set_name = saves.get_current_set()
        level = saves.get_current_level()

        self.controller.init_game(set_name, level)

    def init_select_level(self, _):
        """Pályaválasztó betöltése
        """
        set_name = saves.get_current_set(self.selected_player_id)
        LevelSelectorContainer(self, self.select_level, set_name, self.selected_player_id, size=self.screen.get_size())

    def select_level(self, level: int):
        """Pálya kiválasztásakor lefutó metódus

        Args:
            level (int): kiválasztott pálya száma
        """
        saves.set_current_level(level)

    def init_select_set(self, _):
        """Pályakészletválasztó betöltése
        """
        SetSelectorContainer(self, self.select_set, size=self.screen.get_size())
        
    def select_set(self, set_name: str):
        """Pályakészlet kiválasztásakor lefutó metódus

        Args:
            set_name (str): kiválasztott pályakészlet neve
        """
        saves.set_current_set(set_name)
        saves.set_current_level(0)

    def init_rename_player(self, _):
        """Játékos átnevezésének betöltése
        """
        name = saves.get_player(self.selected_player_id)
        TextEntryContainer(self, "Név", self.rename_player, name, size=self.screen.get_size())

    def rename_player(self, name: str | None):
        """Játékos átnevezése

        Args:
            name (str | None): játékos neve
        """
        if name is None or name == "":
            return

        saves.add_player(name, self.selected_player_id)
        self.player_label.text = f"Játékos: {name}"

    def init_delete_player(self, _):
        """Játékos törlése előtti megerősítése betöltése
        """
        SelectContainer(self, "Biztos törlöd a játékost?", self.delete_player, size=self.screen.get_size())

    def delete_player(self, delete: bool):
        """Játékos törlése

        Args:
            delete (bool): törlés
        """
        if delete:
            saves.remove_player(self.selected_player_id)
            self.back(None)

    def back(self, _):
        """Visszalépés a főmenübe
        """
        menu = self.controller.init_main_menu()
        menu.init_game_slot_selector_menu(None)