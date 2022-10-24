""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: button.py
Verzió: 1.0.0
--------------------
pygame_menu.components.button

Nyomógombként, vagy választható menüelemként felhasználható componens.

Osztályok:
    Button
"""
from __future__ import annotations

import pygame as pg

from sokoban import config
from utils import Pair

from .component import *

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable

class Button(MouseGrabber, Selectable, Component):
    """Container osztályban felhasználható nyomógomb vagy választható menüelem.

    Attributes:
        action (callable): a gomb kiválasztására lefutó metódus
        text (property) (str): a gombon megjelenő szöveg
        font (property) (pygame.font.Font): a gomb betűtipusa
    """
    def __init__(self, container: Container, text: str, action: Callable, selected: bool = False,
        font_size: int = config.DEFAULT_FONT_SIZE, **kwargs):
        """Button

        Args:
            container (Container): a befoglaló container
            text (str): a gombon megjelenő szöveg
            action (Callable): a gomb kiválasztásakor lefutó metódus
            selected (bool, optional): a gomb kiválasztott állapotban inicializálódik. Defaults to False.
            font_size (int, optional): a gomb betűmérete. Defaults to config.DEFAULT_FONT_SIZE.

        Kwargs:
            -> Component.__init__(...)
        """
        Component.__init__(self, container, **kwargs)

        self.action = action
        self.text = text
        self.select = selected
        self.font = config.get_font(config.BUTTON_FONT, font_size)

        self.color['bg'] = config.BUTTON_DEFAULT_COLOR
        self.color['focus'] = config.BUTTON_FOCUS_COLOR
        self.color['select'] = config.BUTTON_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR
        self.color['font_focus'] = config.BUTTON_FONT_FOCUS_COLOR
        self.color['font_select'] = config.BUTTON_FONT_SELECT_COLOR

        if self.select:
            self.container.selected = self

    @property
    def text(self) -> str:
        """getter"""
        return self._text

    @text.setter
    def text(self, value: str):
        """setter

        Raises:
            ValueError: Ha nem str típusú"""
        ex.arg_type_exception('value', value, str)

        self._text = value
        # Ha a régi méret egyenlő a kép méretével akkor nincs előre beállított
        # méret. Az új méret a kép mérete lesz.
        if self.size == (0, 0) or self.size == Pair(self.image.get_size()):
            # A font inicializálása után
            if hasattr(self, "_font"):
                self.size = Pair(self.font.size(self._text)) + Pair(10,10)

        self.updated()

    @property
    def font(self) -> pg.font.Font:
        """getter"""
        return self._font

    @font.setter
    def font(self, value: pg.font.Font):
        """setter
        
        Raises:
            ValueError: Ha nem pygame.font.Font osztály leszármazottja"""
        ex.arg_instance_exception('value', value, pg.font.Font)
        
        self._font = value
        self.text = self._text

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface(self.size, pg.SRCALPHA)

        if self.select:
            self.image.fill(self.color['select'])
            font_color = self.color['font_select']
        elif self.focus:
            self.image.fill(self.color['focus'])
            font_color = self.color['font_focus']
        else:
            self.image.fill(self.color['bg'])
            font_color = self.color['font']

        rendered = self.font.render(self.text, True, font_color)
        self.image.blit(rendered, (5, 5))

    def e_MouseButtonUp(self, **kwargs):
        """Egérgom felengedésének lekezelése"""
        self.click()

    def e_KeyUp(self, key, **kwargs):
        """Enter billentyű felengedésének lekezelése"""
        if self.select and key in (pg.K_RETURN, pg.K_KP_ENTER):
            self.click()

    def click(self):
        """action metódus végigjárása"""
        if callable(self.action):
            self.action(self)