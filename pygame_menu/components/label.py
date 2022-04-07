"""Label osztály modulja.
"""
from __future__ import annotations

import pygame as pg

import config #TODO: refactiring

from .component import *
from utils import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Label(Component):
    """Label osztály.

    Container osztályban felhasználható címke.
    
    Attributes:
        text(property): str a gombbon megjelenő szöveg
        font(property): pg.font.Font a gomb betűtipusa"""
    def __init__(self, container: Container, text: str, *args, **kwargs):
        """belépési pont
        
        Args:
            container: a befogalaló container
            text: a gombon megjelenő szüveg
            kwargs: {position, size, sticky}"""
        Component.__init__(self, container, *args, **kwargs)
        
        self.text = text
        self.font = config.get_font(config.LABEL_FONT, config.DEFAULT_FONT_SIZE)

        self.color['bg'] = config.LABEL_DEFAULT_COLOR
        self.color['font'] = config.LABEL_FONT_COLOR

    @property
    def text(self) -> str:
        """getter"""
        return self._text

    @text.setter
    def text(self, value: str):
        """setter"""
        assert type(value) == str, (f"Várt str típus, kapott {type(value)}")
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
        """setter"""
        assert type(value) == pg.font.Font, (f"Várt pygame.font.Font típus, "
            f"kapott {type(value)}")
        
        self._font = value
        self.text = self._text

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.image.fill(self.color['bg'])

        rendered = self.font.render(self.text, True, self.color['font'])
        self.image.blit(rendered, (0,0))
