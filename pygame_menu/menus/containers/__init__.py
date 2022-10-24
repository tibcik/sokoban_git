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
pygame_menu.menus.containers

Különböző előre definiált Containerek.

Pl.: TextEntryContainer: szövegbekérő mezővel ellátott container
SelectContainer: Igen/Nem választó kontainer

Osztályok:
    ExtendedContainer
    TextEntryContainer
    SelectContainer
    LevelSelectorContainer
    SetSelectorContainer
"""
from __future__ import annotations

import pygame as pg
from math import ceil, floor

from sokoban.data import loader, saves
from utils.asserts import *

from ...components import Container, Label, TextEntry, Button
from ...components.component import STICKY_CENTER, STICKY_LEFT, STICKY_RIGHT, STICKY_UP
from ...sokoban_components import SLevel, SSet

import utils.exceptions as ex

from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
    from ...menu import Menu

class ExtendedContainer:
    """Container osztály kiterjesztésére szolgáló osztály"""
    def save_session(self, clear = False):
        """Menu osztály aktuális állapotának mentése

        Args:
            clear (bool, optional): meglévő Container osztályok törlése a Menu-ből. Defaults to False.

        Raises:
            TypeError: Ha nem a Container osztály leszármazottja
        """
        ex.instance_exception(self, Container)

        self._prev_selected = None
        self._prev_default = None
        self._containers = []

        if self.menu.selected is not None:
            self._prev_selected = self.menu.selected
            self.menu.selected.select = False
        if self.menu.default is not None:
            self._prev_default = self.menu.default
            self.menu.set_default(self)

        self._prev_session = None
        if clear:
            self._prev_session = pg.sprite.Group()
            for container in self.menu.containers:
                if container != self:
                    self._prev_session.add(container)
                    self.menu.containers.remove(container)

    def add_container(self, containers: tuple(Container)):
        """Új Container osztályok hozzáadása

        Args:
            containers (tuple): Container osztályok, az első lesz a kiválasztott
        
        Raises:
            TypeError: Ha nem a Container osztály leszármazottja
            ValueError: Ha nem listaszerű elem
            IndexError: Ha a lista elemszáma kevesebb mint 1
        """
        ex.instance_exception(self, Container)
        ex.arg_index_exception('containers', containers, 1)

        self._containers = [containers[0]]
        
        self.menu.selected = containers[0]
        containers[0].select = True

    def restore_session(self):
        """Menu osztály állapotának visszaállítása
        
        Raises:
            TypeError: Ha nem a Container osztály leszármazottja
        """
        ex.instance_exception(self, Container)
        
        if not hasattr(self, '_prev_selected'):
            return

        if self._prev_session is not None:
            self.menu.containers.add(self._prev_session)

        if self._prev_selected is not None:
            self._prev_selected.select = True
        if self._prev_default is not None:
            self.menu.set_default(self._prev_default)

        self.menu.selected = self._prev_selected
        for container in self._containers:
            self.menu.remove(container)

class TextEntryContainer(ExtendedContainer, Container):
    """Szövegbekérő mező

    Arguments:
        action (callable): visszatérési metódus
        label (Label): a szövegbekérő mező címkéje
        text_entry (TextEntry): a szövegbekérő mező
        cancel_button (Button): mégse gomb
        ok_button (Button): rendben gomb
    """
    def __init__(self, menu: Menu, label: str, action: Callable, default: str = "", cancel: str = "Vissza", ok: str = "Rendben", **kwargs):
        """TextEntryContainer

        Args:
            menu (Menu): objektum amiben a container van
            label (str): a szövegbekérő mező címkéje
            action (Callable): visszatérési metódus
            default (str, optional): szövegmező kezdő értéke. Defaults to "".
            cancel (str, optional): mégse gomb szövege. Defaults to "Vissza".
            ok (str, optional): rendben gomb szövege. Defaults to "Rendben".
        
        Kwargs:
            -> Component.__init__(...)"""
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.label = Label(self, label, position=(1/2,20), sticky=STICKY_UP)
        self.text_entry = TextEntry(self, default, position=(1/2,80), sticky=STICKY_UP, size=(180,32))
        self.cancel_button = Button(self, cancel, self.call_action, position=(1/2-30,160), sticky=STICKY_RIGHT)
        self.ok_button = Button(self, ok, self.call_action, position=(1/2+30,160), sticky=STICKY_LEFT)

        self.color = (0,0,0,128)

        self.save_session()
        self.add_container([self])

        self.menu.fixed = True

        self.sticky = STICKY_CENTER
        self.position = (self.size.p1 / 2, self.size.p2 / 3 )
        self.size[1] = 200

    def call_action(self, button: Button):
        """Gombnyomásra lefutó metódus

        Args:
            button (Button): lenyomott gomb
        """
        self.menu.fixed = False

        self.restore_session()

        if button == self.cancel_button:
            value = None
        else:
            value = self.text_entry.value

        if callable(self.action):
            self.action(value)

class SelectContainer(ExtendedContainer, Container):
    """Igen/Nem választó Container

    Arguments:
        action (callable): visszatérési metódus
        label (Label): a szövegbekérő mező címkéje
        cancel_button (Button): mégse gomb
        ok_button (Button): rendben gomb
    """
    def __init__(self, menu: Menu, label: str, action: Callable, cancel: str = "Vissza", ok: str = "Rendben", **kwargs):
        """SelectContainer

        Args:
            menu (Menu): objektum amiben a container van
            label (str): a szövegbekérő mező címkéje
            action (Callable): visszatérési metódus
            cancel (str, optional): mégse gomb szövege. Defaults to "Vissza".
            ok (str, optional): rendben gomb szövege. Defaults to "Rendben".
        
        Kwargs:
            -> Component.__init__(...)"""
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.label = Label(self, label, position=(1/2,20), sticky=STICKY_UP)
        self.cancel_button = Button(self, cancel, self.call_action, position=(1/2-30,80), sticky=STICKY_RIGHT)
        self.ok_button = Button(self, ok, self.call_action, position=(1/2+30,80), sticky=STICKY_LEFT)

        self.color = (0,0,0,128)

        self.save_session()
        self.add_container([self])

        self.menu.fixed = True

        self.sticky = STICKY_CENTER
        self.position = (self.size.p1 / 2, self.size.p2 / 3 )
        self.size[1] = 120

    def call_action(self, button):
        """Gombnyomásra lefutó metódus

        Args:
            button (Button): lenyomott gomb
        """
        self.menu.fixed = False
        
        self.restore_session()

        if button == self.cancel_button:
            value = False
        else:
            value = True

        if callable(self.action):
            self.action(value)

class LevelSelectorContainer(ExtendedContainer, Container):
    """Szint választó Container

    Arguments:
        action (callable): visszatérési metódus
        set_name (str): pályakészlet neve
        selected_player_id (id): kiválasztott játékos
        set_info (dict): {"name": (str), "dificulty": (int), "description": (str)}
        list_container (Container): a pályákat tartalmazó container
        spaces (list[Space]): játékterek
    """
    def __init__(self, menu: Menu, action: Callable, set_name: str, show_info: bool = True, selected_player_id: int = -1, **kwargs):
        """LevelSelectorContainer

        Args:
            menu (Menu): objektum amiben a container van
            action (Callable): visszatérési metódus
            set_name (str): pályakészlet neve
            selected_player_id (int, optional): kiválasztott játékos, ha -1 akkor bármelyik pálya választható. Defaults to -1.

        Kwargs:
            -> Component.__init__(...)
        """
        Container.__init__(self, menu, **kwargs)

        self.action = action

        self.show_info = show_info

        self.save_session(True)

        self.set_name = set_name
        self.selected_player_id = selected_player_id
        self.set_info = loader.jget_info(None, self.set_name)

        (rows, _) = self.get_dim()
        x_pos = int(self.size.p1 / 8)
        y_pos = int((self.size.p2 - (rows * 400)) / 2)
        self.list_container = Container(self.menu, position=(x_pos,y_pos), size=(self.size[0] * 6/8, rows*410))
        self.list_container.color['bg'] = (0,0,0,0)
        self.list_container.color['focus'] = (0,0,0,0)
        self.list_container.color['select'] = (0,0,0,0)
        
        self.add_container((self.list_container, self))

        self.spaces = []
        self.init_spaces()

    def get_dim(self) -> tuple[int, int]:
        """kirajzoláshoz szükséges sorok, oszlopok száma

        Returns:
            tuple[int, int]: kirajzoláshoz szükséges sorok, oszlopok száma
        """
        rows = floor((self.size[1] * 6/8) / 400)
        rows = max(rows, 1)
        cols = ceil(loader.jget_levels() / rows)

        return (rows, cols)

    def init_spaces(self):
        """játékterek betöltése
        """
        (_, cols) = self.get_dim()

        row = 0
        col = 0

        for level in range(loader.jget_levels()):
            action = self.select_level
            if self.selected_player_id != -1:
                stat = saves.get_set_statistic(self.set_name)
                done_levels = 0 if stat is None else stat['done_levels']
                if level > done_levels:
                    action = None
            SLevel(self.list_container, action, self.set_name, level, self.show_info, position=(col*228, 400*row))
            col += 1
            if col > cols:
                row += 1
                col = 0

        Label(self, self.set_info['name'], position=(1/8, 1/32))
        Button(self, "Vissza", self.back, position=(1/8, 14/16))

    def select_level(self, slevel: SLevel):
        """Pálya kiválasztásaok lefutó metódus

        Args:
            slevel (SLevel): kiválasztott SLevel objektum
        """
        self.back(None)

        if callable(self.action):
            self.action(slevel.level)

    def back(self, _):
        """Visszatérés az előző munkamenethez
        """
        self.restore_session()

class SetSelectorContainer(ExtendedContainer, Container):
    """Pályakészlet választó Container

    Arguments:
        action (callable): visszatérési metódus
        sets (tuple[str]): pályakészletek nevei
        list_container (Container): a pályákat tartalmazó container
        spaces (list[Space]): játékterek
    """
    def __init__(self, menu: Menu, action: Callable, show_info: bool = True, **kwargs):
        """SetSelectorContainer

        Args:
            menu (Menu): objektum amiben a container van
            action (Callable): visszatérési metódus

        Kwargs:
            -> Component.__init__(...)
        """
        Container.__init__(self, menu, **kwargs)

        self.action = action
        self.show_info = show_info

        self.save_session(True)

        self.sets = loader.jget_sets()

        (rows, _) = self.get_dim()
        x_pos = int(self.size.p1 / 8)
        y_pos = int((self.size.p2 - (rows * 400)) / 2)
        self.list_container = Container(self.menu, position=(x_pos,y_pos), size=(self.size[0] * 6/8, rows*410))

        self.list_container.color['bg'] = (0,0,0,0)
        self.list_container.color['focus'] = (0,0,0,0)
        self.list_container.color['select'] = (0,0,0,0)
        
        self.add_container((self.list_container, self))
        #self.menu.fixed = True

        self.spaces = []
        self.init_spaces()

    def get_dim(self) -> tuple[int,int]:
        """kirajzoláshoz szükséges sorok, oszlopok száma

        Returns:
            tuple[int, int]: kirajzoláshoz szükséges sorok, oszlopok száma
        """
        rows = floor((self.size[1] * 6/8) / 400)
        rows = max(rows, 1)
        cols = ceil(len(self.sets) / rows)

        return (rows, cols)

    def init_spaces(self):
        """játékterek betöltése
        """
        (_, cols) = self.get_dim()

        row = 0
        col = 0

        for set_name in self.sets:
            SSet(self.list_container, self.select_set, set_name, self.show_info, position=(col*228, 400*row))
            col += 1
            if col > cols:
                row += 1
                col = 0

        Label(self, "Pályakészletek", position=(1/8, 1/32))
        Button(self, "Vissza", self.back, position=(1/8, 14/16))

    def select_set(self, sset: SSet):
        """Pályakészlet kiválasztásakor lefutó metódus

        Args:
            sset (SSet): kiválasztott SSet objektum
        """
        self.back(None)
        
        if callable(self.action):
            self.action(sset.set_name)

    def back(self, _):
        """Visszatérés az előző munkamenethez
        """
        self.restore_session()