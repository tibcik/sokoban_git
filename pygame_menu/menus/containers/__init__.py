"""Különböző előre definiált Containerek.

Pl.: TextEntryContainer: szövegbekérő mezővel ellátott container
SelectContainer: Igen/Nem választó kontainer
"""
from __future__ import annotations
from math import ceil, floor
from subprocess import call

import pygame as pg

import config #TODO: refactoring
from pygame_menu.components.component import STICKY_CENTER, STICKY_LEFT, STICKY_RIGHT, STICKY_UP
from pygame_menu.sokoban_components.slevel import SLevel

from ...components import Container, Label, TextEntry, Button

import config.saves as saves
import game.game.loader as loader

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ...menu import Menu

class TextEntryContainer(Container):
    def __init__(self, menu: Menu, label: str, action: Callable, default: str = "", cancel: str = "Vissza", ok: str = "Rendben", **kwargs):
        """belépési pont
        
        Args:
            menu: pygame_menu.Menu objektum
            kwargs: {position, size, sticky}"""
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.label = Label(self, label, position=(1/2,20), sticky=STICKY_UP)
        self.text_entry = TextEntry(self, default, position=(1/2,80), sticky=STICKY_UP, size=(180,32))
        self.cancel_button = Button(self, cancel, self.call_action, position=(1/2-30,160), sticky=STICKY_RIGHT)
        self.ok_button = Button(self, ok, self.call_action, position=(1/2+30,160), sticky=STICKY_LEFT)

        self.color = (0,0,0,128)

        self.prev_selected = None

        if self.menu.selected is not None:
            self.prev_selected = self.menu.selected
            self.menu.selected.select = False
        
        self.menu.selected = self
        self.select = True
        self.menu.fixed = True

        self.sticky = STICKY_CENTER
        self.position = (self.size.p1 / 2, self.size.p2 / 3 )
        self.size[1] = 200

    def call_action(self, button):
        if self.prev_selected is not None:
            self.prev_selected.select = True
        
        self.menu.fixed = False
        self.menu.selected = self.prev_selected
        self.menu.remove(self)

        if button == self.cancel_button:
            value = None
        else:
            value = self.text_entry.value

        if callable(self.action):
            self.action(value)

class SelectContainer(Container):
    def __init__(self, menu: Menu, label: str, action: Callable, cancel: str = "Vissza", ok: str = "Rendben", **kwargs):
        """belépési pont
        
        Args:
            menu: pygame_menu.Menu objektum
            kwargs: {position, size, sticky}"""
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.label = Label(self, label, position=(1/2,20), sticky=STICKY_UP)
        self.cancel_button = Button(self, cancel, self.call_action, position=(1/2-30,80), sticky=STICKY_RIGHT)
        self.ok_button = Button(self, ok, self.call_action, position=(1/2+30,80), sticky=STICKY_LEFT)

        self.color = (0,0,0,128)

        self.prev_selected = None

        if self.menu.selected is not None:
            self.prev_selected = self.menu.selected
            self.menu.selected.select = False
        
        self.menu.selected = self
        self.select = True
        self.menu.fixed = True

        self.sticky = STICKY_CENTER
        self.position = (self.size.p1 / 2, self.size.p2 / 3 )
        self.size[1] = 120

    def call_action(self, button):
        if self.prev_selected is not None:
            self.prev_selected.select = True
        
        self.menu.fixed = False
        self.menu.selected = self.prev_selected
        self.menu.remove(self)

        if button == self.cancel_button:
            value = False
        else:
            value = True

        if callable(self.action):
            self.action(value)

class LevelSelectorContainer(Container):
    def __init__(self, menu: Menu, action: Callable, set_name: str, selected_player_id: int = -1, **kwargs):
        """belépési pont
        
        Args:
            menu: pygame_menu.Menu objektum
            kwargs: {position, size, sticky}"""
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.prev_selected = None

        if self.menu.selected is not None:
            self.prev_selected = self.menu.selected
            self.menu.selected.select = False
        
        self.menu.selected = self
        self.select = True
        self.menu.fixed = True

        self.set_name = set_name
        self.selected_player_id = selected_player_id
        self.set_info = loader.jget_info(None, self.set_name)

        self.spaces = []
        self.init_spaces()

    def init_spaces(self):
        rows = floor((self.size[1] * 6/8) / 400) #TODO a floor-nál van jobb megoldás
        rows = max(rows, 1)
        cols = ceil(loader.jget_levels() / rows)

        row = 0
        col = 0

        for level in range(loader.jget_levels()):
            action = self.select_level
            if self.selected_player_id != -1:
                stat = saves.get_set_statistic(self.set_name)
                done_levels = 0 if stat is None else stat['done_levels']
                if level > done_levels:
                    action = None
            SLevel(self, action, self.set_name, level, position=(1/8+col*228, 1/8+400*row))
            col += 1
            if col > cols:
                row += 1
                col = 0

        Label(self, self.set_info['name'], position=(1/8, 1/32))
        Button(self, "Vissza", self.back, position=(1/8, 14/16))

    def select_level(self, slevel):
        print("NotImplemented")

    def back(self, _):
        if self.prev_selected is not None:
            self.prev_selected.select = True
        
        self.menu.fixed = False
        self.menu.selected = self.prev_selected
        self.menu.remove(self)