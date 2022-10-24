""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: label.py
Verzió: 1.0.0
--------------------
pygame_menu.components.label

Címke menüelem.

Osztályok:
    Label
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *
from utils import Pair

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Label(Component):
    """Label osztály.

    Container osztályban felhasználható címke.
    
    Attributes:
        text(property) (str): a gombbon megjelenő szöveg
        font(property) (pygame.font.Font): a gomb betűtipusa"""
    def __init__(self, container: Container, text: str, font_size = config.DEFAULT_FONT_SIZE, **kwargs):
        """belépési pont
        
        Args:
            container (Container): a befogalaló container
            text (str): a gombon megjelenő szüveg
            font_size (int): a szöveg mérete. Defaults to config.DEFAULT_FONT_SIZE.
        
        Kwargs:
            -> Component.__init__(...)"""
        Component.__init__(self, container, **kwargs)
        
        self.text = text
        self.font = config.get_font(config.LABEL_FONT, font_size)

        self.color['bg'] = config.LABEL_DEFAULT_COLOR
        self.color['font'] = config.LABEL_FONT_COLOR

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
        self.image.fill(self.color['bg'])

        rendered = self.font.render(self.text, True, self.color['font'])
        self.image.blit(rendered, (0,0))
