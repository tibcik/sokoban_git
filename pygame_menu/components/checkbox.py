"""Checkbox osztály modul
"""
from __future__ import annotations

import pygame as pg

import config #TODO: refactiring

from .component import *
from utils import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Checkbox(MouseGrabber, Selectable, Component):
    """Checkbox osztály.

    Container osztályban felhasználható választóelem.
    
    Attributes:
        checked(property): a kiválasztás állapota"""
    def __init__(self, container: Container, checked: bool = False, **kwargs):
        """belépési pont
        
        Args:
            container: a befogalaló container
            checked: a kiválasztás állapota"""
        Component.__init__(self, container, **kwargs)

        self.checked = checked

        self.size = (15, 15)

        self.color['bg'] = config.CHECKBOX_DEFAULT_COLOR
        self.color['focus'] = config.CHECKBOX_FOCUS_COLOR
        self.color['select'] = config.CHECKBOX_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR

    @property
    def checked(self) -> bool:
        """getter"""
        return self._checked

    @checked.setter
    def checked(self, value: bool):
        """setter"""
        assert type(value) == bool, (f"Várt bool típus, kapott {type(value)}")
        self._checked = value

        self.updated()

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface(self.size, pg.SRCALPHA)

        if self.select:
            self.image.fill(self.color['select'])
        elif self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])

        pg.draw.rect(self.image, self.color['font'], (1,1,13,13), 1)
        if self.checked:
            pg.draw.line(self.image, self.color['font'], (0,0), (15,15))
            pg.draw.line(self.image, self.color['font'], (15,0), (0,15))

    def e_MouseButtonUp(self, **kwargs):
        """Egérgom felengedésének lekezelése"""
        self.checked = not self.checked

    def e_KeyUp(self, key, **kwargs):
        """Enter billentyű felengedésének lekezelése"""
        if self.select and key in (pg.K_RETURN, pg.K_KP_ENTER):
            self.checked = not self.checked