"""Scrollbar osztály modulja
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *
from ..utils import VERTICAL, HORIZONTAL
from utils import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Scrollbar(MouseGrabber, Component):
    """Scrollbar osztály.

    Container osztályban felhasználható nyomógomb vagy választható menüelem.
    
    Attributes:
        orientation (int): HORIZONTAL | VERTICAL a scrollbar iránya
        bar_rect (pygame.rect.Rect): a bart befoglaló négyszög
        view_size (Pair): a Container image mérete
        value (float): a scrollbar értéke 0 és 1 között
        focus(property) (bool):  componens fokuszban van-e
        show(property) (bool): a componens látható-e"""
    def __init__(self, container: Container, orientation: int = VERTICAL, **kwargs):
        """belépési pont
        
        Args:
            container (Container): a befogalaló container
            orientation (int): a scrollbar iránya. Defaults to VERTICAL.
        
        Kwargs:
            -> Component.__init__(...)"""
        Component.__init__(self, container, **kwargs)

        self.orientation = orientation
        self.bar_rect = pg.rect.Rect(0,0,0,0)

        self.view_size = Pair(self.container.image.get_size())

        self.value = 0.0
        self.show = False

        self.color['bg'] = config.SCROLLBAR_DEFAULT_COLOR
        self.color['focus'] = config.SCROLLBAR_FOCUS_COLOR
        self.color['bar'] = config.SCROLLBAR_BAR_COLOR

        # A scrollbar csak a bal felső pontjához lehet igazítva
        self.sticky = STICKY_UPLEFT

    @property
    def focus(self) -> bool:
        """getter"""
        return self._focus

    @focus.setter
    def focus(self, value: bool):
        """setter"""
        self._focus = value

        # Ha még nincs inicializálva az orientation akkor az ős osztály hívta
        # meg...
        if hasattr(self, "orientation"):
            self.view_size = Pair(self.container.image.get_size())

        self.updated()

    @property
    def show(self) -> bool:
        """getter"""
        return self._show

    @show.setter
    def show(self, value: bool):
        """setter"""
        if not hasattr(self, "_show"):
            self._show = value

        # Ha még nincs inicializálva az orientation akkor az ős osztály hívta
        # meg...
        if value and hasattr(self, "orientation"):
            self.view_size = Pair(self.container.image.get_size())

        if self._show != value:
            self.updated()

        self._show = value

    def calc_position(self) -> None:
        """A scrollbar pozíciójának beállítása
        
        A scrollbar pozíciója függ attól, hogy fókuszban van-e és az őt befoglaló
        container méretetitől."""
        mod = Pair(0, 0)
        if self.focus:
            mod += (0, -4) if self.orientation == HORIZONTAL else (-4, 0)

        x = (self.container.scroll[0] if self.orientation == HORIZONTAL else 
            self.container.size[0] - 7 + self.container.scroll[0])
        y = (self.container.size[1] - 7 + self.container.scroll[1] if
            self.orientation == HORIZONTAL else self.container.scroll[1])

        self.position = Pair(x, y) + mod

    def calc_size(self) -> None:
        """A scrollbar méretének beállítása
        
        A scrollbar mérete függ attól, hogy fókuszban van-e és az őt befoglaló
        container méretetitől."""
        mod = Pair(0, 0)
        if self.focus:
            mod += (0, 4) if self.orientation == HORIZONTAL else (4, 0)

        width = (self.container.size[0] - 7 if self.orientation == HORIZONTAL else 7)
        height = (7 if self.orientation == HORIZONTAL else self.container.size[1] - 7)

        self.size = Pair(width, height) + mod

    def calc_bar_data(self) -> None:
        """A scrollbar bar adatainak beállítása"""
        selector = 0 if self.orientation == HORIZONTAL else 1
        
        # Ha hiba lenne(pl.: nullával osztás) a scrollbardt elrejtjük
        if (self.container.image.get_size()[selector] == 0 or
            self.container.image.get_size()[selector] == self.container.size[selector]):
            self.show = False
            return

        # A scroll értéke 0 és 1 között
        self.value = (self.container.scroll[selector] / 
            (self.container.image.get_size()[selector] - self.container.size[selector]))

        # Arányszám, a látható és a nem látható területekhez viszonyítva
        rate = (0 if self.container.image.get_size()[selector] == 0 else
            (self.container.size[selector] / self.container.image.get_size()[selector]))
    
        # A bar mérete a teljes méret * az arányszámmal
        bar_size = Pair(1, 1)
        bar_size[selector] = rate
        bar_size *= self.size
        bar_size[(selector - 1) * -1] -= 2

        # A bar pozíciója
        bar_pos = Pair(1, 1)
        bar_pos[selector] = (self.size[selector] - bar_size[selector]) * self.value

        self.bar_rect = pg.rect.Rect(bar_pos, bar_size)

    def update_image(self, other = False):
        """Kirajzolandó kép frissítése."""
        # Ha valamelyik scrollbar frissűl szükséges a másikat is frissíteni,
        # hogy jó helyen legyen kirajzolva.
        if not other:
            scroller = "yscroller" if self.orientation == HORIZONTAL else "xscroller"
            getattr(self.container, scroller).update_image(True)
        self.calc_position()
        self.calc_size()
        self.calc_bar_data()
        # print("Scrollbar", self.orientation, self.position, self.size, self.show, self.value, self.bar_rect) # TODO: debug miatt, ki kell venni

        self.image = pg.Surface(self.size, pg.SRCALPHA)
        if self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])
        
        rect = pg.Surface(self.bar_rect.size)
        rect.fill(self.color['bar'])

        self.image.blit(rect, self.bar_rect)

    def e_MouseWheel(self, y, **kwargs):
        """egér görgőjének továbbadása
        
        Args:
            y (int): görgő y elmozdulása
        
        Kwargs:
            witch (?): ?
            flipped (?): ?
            x (int): görgő x elmozdulása
            touch (bool): ?"""
        self.container.scroll = {'relx' if self.orientation == HORIZONTAL else 'rely': 25 * y * -1}

        self.updated()

    def e_MouseButtonDown(self, pos, **kwargs):
        """Egérgom felengedésének lekezelése
        
        Args:
            pos (tuple): az mutató pozíciója
            
        Kwargs:
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        bar_pos, bar_size = self.bar_rect.topleft, self.bar_rect.size
        i = 0 if self.orientation == HORIZONTAL else 1

        if bar_pos[i] < pos[i] and (bar_pos[i] + bar_size[i]) > pos[i]:
            self.grab_mouse()

    def e_MouseMotion(self, rel, **kwargs):
        """egér mozgás kezelése
        
        Args:
            rel (tuple): az egér relatív elmozdulása
            
        Kwargs:
            pos (tuple): az mutató pozíciója
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        if self.mouse_grabbed:
            selector = 0 if self.orientation == HORIZONTAL else 1
            rate = (self.view_size[selector] - self.size[selector]) / (self.size[selector] - self.bar_rect.size[selector])
            self.container.scroll = {'relx' if self.orientation == HORIZONTAL else 'rely': rel[selector] * rate}

            self.updated()