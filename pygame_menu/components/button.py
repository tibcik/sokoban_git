"""Button osztály.

Nyomógombként, vagy választható menüelemként felhasználható componens.
"""
from __future__ import annotations

import pygame as pg

import config #TODO: refactiring

from .component import *
from utils import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable

class Button(MouseGrabber, Selectable, Component):
    """Button osztály.

    Container osztályban felhasználható nyomógomb vagy választható menüelem.
    
    Attributes:
        action: callabel a gomb kiválasztására lefutó metódus
        text(property): str a gombbon megjelenő szöveg
        font(property): pg.font.Font a gomb betűtipusa"""
    def __init__(self, container: Container, text: str, action: Callable, selected: bool = False, **kwargs):
        """belépési pont
        
        Args:
            container: a befogalaló container
            text: a gombon megjelenő szüveg
            action: a gomb kiválasztásakor lefuttandó metódus
            kwargs: {position, size, sticky}"""
        Component.__init__(self, container, **kwargs)

        self.action = action
        self.text = text
        self.select = selected
        self.font = config.get_font(config.BUTTON_FONT, config.DEFAULT_FONT_SIZE)

        self.color['bg'] = config.BUTTON_DEFAULT_COLOR
        self.color['focus'] = config.BUTTON_FOCUS_COLOR
        self.color['select'] = config.BUTTON_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR

        if self.select:
            self.container.selected = self

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
        #assert type(value) == pg.font.Font, (f"Várt pygame.font.Font típus, "
        #    f"kapott {type(value)}") #TODO ez nem működik
        
        self._font = value
        self.text = self._text

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface(self.size, pg.SRCALPHA)

        if self.select:
            self.image.fill(self.color['select'])
        elif self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])

        rendered = self.font.render(self.text, True, self.color['font'])
        self.image.blit(rendered, (5, 5))

    #TODO: animált kiválasztás

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