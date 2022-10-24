""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: sset.py
Verzió: 1.0.0
--------------------
pygame_menu.sokoban_componenets.sset

Set választó osztály modulja

Nem tisztán menüelem, mivel a működéséhez szükséges a sokoban játék néhány osztálya.
"""
from __future__ import annotations

import pygame as pg

from sokoban import config
from sokoban.data import loader, saves
from sokoban import Space

from ..components.component import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable

class SSet(MouseGrabber, Selectable, Component):
    """SSet osztály.

    Container osztályban felhasználható szet adatai kijelző menüelem. Lehet 
    választható.
    
    Attributes:
        action (Callable): a kiválasztáskor lefuttadandó metódus
        set_name (str): pályakészket neve
        set_info (dict): {"name": str, "dificulty": int, "description": str}
        stats (dict): {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float), 'done_levels': int}
        level_image (pygame.Surface): a pálya képe
        font(property) (pygame.font.Font): betűtipus"""
    def __init__(self, container: Container, action: Callable, set_name: str,
        show_info: bool = True, **kwargs):
        """SSet

        Args:
            container (Container): a befogalaló container
            action (Callable): visszatérési metódus
            set_name (str): pályakészlet neve
            level (int): szint száma
        """
        Component.__init__(self, container, **kwargs)

        assert callable(action), f"Vár calabble típus, kapott {type(action)}"
        self.action = action
        self.set_name = set_name

        self.font = config.get_font(config.BUTTON_FONT, config.SMALL_FONT_SIZE)

        self.set_info = loader.jget_info(None, self.set_name)
        assert self.set_info is not None, (f"Hibás set_nam vagy level: "
            f"{set_name}.")

        self.stats = None
        if show_info:
            self.stats = saves.get_set_statistic(self.set_name)

        self.size = (228, 400) #TODO padding, margin

        self.color['bg'] = config.BUTTON_DEFAULT_COLOR
        self.color['focus'] = config.BUTTON_FONT_FOCUS_COLOR
        self.color['select'] = config.BUTTON_FONT_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR

        if 'selected' in kwargs and kwargs['selected']:
            self.select = True
        else:
            self.select = False

        self.level_image = pg.Surface((200,200))
        space = Space((200,200), None, self.set_name, 0)
        space.draw(self.level_image)

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

        # Pályák képének kirajzolása
        self.image.blit(self.level_image, (14, 14))

        # Név és nehézség
        text = f"{self.set_info['name']} ({self.set_info['dificulty']})"
        rendered = self.font.render(text, True, self.color['font'])
        self.image.blit(rendered, (14, 228))

        # Pályák száma a set-ben és az ezekből elvégzettek száma
        done_levels = self.stats['done_levels'] if self.stats else 0
        text = f"Pályák: {done_levels}/{loader.jget_levels(self.set_name)}"
        rendered = self.font.render(text, True, self.color['font'])
        self.image.blit(rendered, (14, 258))
        
        # Leírás
        lines = self.set_info['description'].split('\n')
        rendered = self.font.render(lines[0], True, self.color['font'])
        self.image.blit(rendered, (14, 288))
        for i in range(1, len(lines)):
            rendered = self.font.render(lines[i], True, self.color['font'])
            self.image.blit(rendered, (14, 288 + i * 30))

    def e_MouseButtonUp(self, **kwargs):
        """egér gombelengedés kezelése
        
        Kwargs:
            pos (tuple): az mutató pozíciója
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        if callable(self.action):
            self.action(self)

    def e_KeyUp(self, key, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        if key in (pg.K_RETURN, pg.K_KP_ENTER) and callable(self.action):
            self.action(self)