""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: editor_main_menu.py
Verzió: 1.0.0
--------------------
pygame_menu.menus.editor_main_menu

Pályaszerkesztő főmenü

Osztályok:
    EditroMainMenu
"""
from __future__ import annotations
import numpy as np

import pygame as pg
from pygame_menu.components.select import Select
from pygame_menu.components.textentry import MultiTextEntry, TextEntry

from sokoban.data import loader

from ..menu import Menu
from ..components import Container, Button, Label
from .containers import LevelSelectorContainer, SetSelectorContainer, TextEntryContainer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class EditorMainMenu(Menu):
    """Pályaszerkesztő főmenü

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        selected_set (str): a kiválasztott pályakészlet neve
        selected_level (int): a kiválasztott pálya száma
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

        self.selected_set = None
        self.selected_level = None

        self.init_main_menu(None)

    def init_main_menu(self, _):
        """Főmenü betöltése
        """
        self.clear()
        self.main_container = Container(self, "profile_back.png", size=self.screen.get_size())

        b = None
        y_offset = 0
        b = Button(self.main_container, "Új pályakészlet", self.init_new_set, position=(1/8,1/3), selected=True)
        y_offset = b.size[1] + 10
        b = Button(self.main_container, "Meglévő pályakészletek", self.show_sets, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30

        Button(self.main_container, "Kilépés", self.controller.exit, position=(1/8,1/3+y_offset))

    def init_new_set(self, _):
        """init_new_set Új pályakészlet nevét bekérő container betöltése
        """
        TextEntryContainer(self, "Pályakészlet neve", self.new_set, position=(0,1/3), size=self.screen.get_size())

    def new_set(self, name: str):
        """new_set Új pályakészlet létrehozása

        Args:
            name (str): pályakészlet neve
        """
        sets = loader.jget_sets()

        if name is None:
            return

        if name == '' or name in sets:
            tec = TextEntryContainer(self, "Pályakészlet neve", self.new_set, position=(0,1/3), size=self.screen.get_size())
            tec.text_entry.value = "Értvénytelen vagy létező pályanév! Adjon meg újjat!"
            return

        loader.jset_info(None, name, set_name = name)
        self.select_set(name)

    def show_sets(self, _):
        """show_sets Pályakészletválasztó betöltése
        """
        SetSelectorContainer(self, self.select_set, False, background="profile_back.png", size=self.screen.get_size())

    def select_set(self, set_name: str):
        """select_set Kiválasztott pályakészlet betöltése

        Args:
            set_name (str): kiválasztott pályakészlet neve
        """
        set_info = loader.jget_info(None, set_name)
        if set_info == None:
            return

        self.selected_set = set_name

        self.init_set_menu(None)

    def init_set_menu(self, _):
        """init_set_menu Pályakészlet menü megjelenítése
        """
        set_info = loader.jget_info(None, self.selected_set)
        
        self.clear()
        self.main_container = Container(self, "profile_back.png", size=self.screen.get_size())

        l = None
        y_offset = 0

        l = Label(self.main_container, f"{set_info['name']}({str(set_info['dificulty'])})", position=(1/8,1/8))
        y_offset += l.size[1] + 5
        lines = set_info['description'].split("\n")
        for line in lines:
            l = Label(self.main_container, line, 14, position=(3/16,1/8+y_offset))
            y_offset += l.size[1]

        b = None
        y_offset = 0
        b = Button(self.main_container, "Új pálya", self.new_level, True, position=(1/8,1/3))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Pálya választása", self.show_levels, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Adatok szerkesztése", self.init_set_info, position=(1/8,1/3+y_offset))
        y_offset += b.size[1] + 30

        Button(self.main_container, "Vissza", self.init_main_menu, position=(1/8,1/3+y_offset))

    def new_level(self, _):
        """new_level Új pálya létrehozása
        """
        levels = loader.jget_levels(self.selected_set)
        
        loader.jset_info(levels, "Új pálya", 0, '', self.selected_set)

        data = np.ones((3,3))
        loader.jset_data(levels, data, self.selected_set)

        self.select_level(levels)

    def show_levels(self, _):
        """show_levels Pályaválasztó betöltése
        """
        LevelSelectorContainer(self, self.select_level, self.selected_set, False, background="profile_back.png", size=self.screen.get_size())

    def select_level(self, level: int):
        """select_level Pálya kiválasztása

        Args:
            level (int): kiválasztott pálya száma
        """
        level_info = loader.jget_info(level)
        if level_info is None:
            self.init_set_menu(None)
            return

        self.selected_level = level

        self.init_level_info(None)

    def init_level_info(self, _):
        """init_level_info Pálya adatait szerkesztő menü betöltése
        """
        level_info = loader.jget_info(self.selected_level)
        levels = loader.jget_levels()

        self.clear()

        container = Container(self, "profile_back.png", size=self.screen.get_size())

        Button(container, "Pálya szerkesztése", self.edit_level, position=(1/8,1/16))

        Label(container, "Név", position=(1/8,3/16))
        self.e_level_name = TextEntry(container, level_info['name'], size=(240,32), position=(3/8,3/16))
        Label(container, "Nehézség", position=(1/8,4/16))
        self.s_level_dif = Select(container, (1,2,3,4,5,6,7,8,9), level_info['dificulty'] - 1, position=(3/8,4/16))
        Label(container, "Leírás", position=(1/8,5/16))
        self.e_level_desc = MultiTextEntry(container, level_info['description'], size=(240,180), position=(3/8,5/16))

        Label(container, "Pálya pozíciója", position=(1/8,5/16+210))
        self.s_level_pos = Select(container, [x for x in range(1,levels+1)], self.selected_level, position=(3/8,5/16+210))

        b = Button(container, "Mentés", self.save_level_info, position=(1/8,7/16+210))
        Button(container, "Vissza", self.init_set_menu, position=(1/8,7/16+b.size.p2+220))

    def save_level_info(self, _):
        """save_level_info Pálya adatainak elmentése
        """
        level_name = self.e_level_name.value
        level_dif = self.s_level_dif.value
        level_desc = self.e_level_desc.value

        level_pos = int(self.s_level_pos.value) - 1
        
        if level_name == '':
            level_info = loader.jget_info(self.selected_level)
            level_name = level_info['name']

        if level_pos != self.selected_level:
            tmp_info = loader.jget_info(level_pos)
            tmp_data = loader.jget_data(level_pos)

            level_data = loader.jget_data(self.selected_level)

            loader.jset_info(self.selected_level, tmp_info['name'], tmp_info['dificulty'], tmp_info['description'], self.selected_set)
            loader.jset_data(self.selected_level, tmp_data, self.selected_set)

            loader.jset_data(level_pos, level_data, self.selected_set)

        loader.jset_info(level_pos, level_name, level_dif, level_desc, self.selected_set)

        delattr(self, "e_level_name")
        delattr(self, "s_level_dif")
        delattr(self, "e_level_desc")
        delattr(self, "s_level_pos")

        self.init_set_menu(None)

    def edit_level(self, _):
        """edit_level Pályaszerkesztő betöltése
        """
        self.controller.init_editor(self.selected_set, self.selected_level)

    def init_set_info(self, _):
        """init_set_info Pályakészlet adatait szerkesztő menü betöltése
        """
        set_info = loader.jget_info(None, self.selected_set)

        self.clear()
        
        container = Container(self, "profile_back.png", size=self.screen.get_size())

        Label(container, "Név", position=(1/8,4/16))
        self.e_set_name = TextEntry(container, set_info['name'], size=(240,32), position=(2/8,4/16))
        Label(container, "Nehézség", position=(1/8,5/16))
        self.s_set_dif = Select(container, (1,2,3,4,5,6,7,8,9), set_info['dificulty'] - 1, position=(2/8,5/16))
        Label(container, "Leírás", position=(1/8,6/16))
        self.e_set_desc = MultiTextEntry(container, set_info['description'], size=(240,180), position=(2/8,6/16))

        b = Button(container, "Mentés", self.save_set_info, position=(1/8,6/16+210))
        Button(container, "Vissza", self.init_set_menu, position=(1/8,6/16+b.size.p2+220))

    def save_set_info(self, _):
        """save_set_info Pályakészlet adatainak elmentése
        """
        set_name = self.e_set_name.value
        set_dif = self.s_set_dif.value
        set_desc = self.e_set_desc.value

        if set_name == '':
            set_info = loader.jget_info(None, self.selected_set)
            set_name = set_info['name']

        loader.jset_info(None, set_name, set_dif, set_desc, self.selected_set)

        delattr(self, "e_set_name")
        delattr(self, "s_set_dif")
        delattr(self, "e_set_desc")
        
        self.init_set_menu(None)