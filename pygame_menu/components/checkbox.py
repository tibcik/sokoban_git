""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: checkbox.py
Verzió: 1.0.0
--------------------
pygame_menu.components.checkbox

Jelölőmezőként használható menüelem.

Osztályok:
    Checkbox
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Checkbox(MouseGrabber, Selectable, Component):
    """Checkbox osztály.

    Container osztályban felhasználható választóelem.
    
    Attributes:
        checked(property) (bool): a kiválasztás állapota"""
    def __init__(self, container: Container, checked: bool = False, **kwargs):
        """belépési pont
        
        Args:
            container (Container): a befogalaló container
            checked (bool): a kiválasztás állapota. Defaults to False.
            
        Kwargs:
            -> Component.__init__(...)"""
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
        """setter
        
        Raises:
            ValueError: Ha nem bool típusú"""
        ex.arg_type_exception('value', value, bool)
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