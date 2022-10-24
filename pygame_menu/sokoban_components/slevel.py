""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: slevel.py
Verzió: 1.0.0
--------------------
pygame_menu.sokoban_componenets.slevel

Szint választó osztály modulja

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

class SLevel(MouseGrabber, Selectable, Component):
    """SLevels osztály.

    Container osztályban felhasználható szint adatai kijelző menüelem. Lehet 
    választható.
    
    Attributes:
        action (Callable): a kiválasztáskor lefuttadandó metódus
        set_name (str): pályakészket neve
        level (int): a szint sorszáma
        level_info (dict): {"name": str, "dificulty": int, "description": str}
        stats (dict): {'moves': (int), 'time': (float), 'best_moves': (int), 'best_time': (float)}
        space_image (pygame.Surface): a pálya képe
        font(property) (pygame.font.Font): betűtipus"""
    def __init__(self, container: Container, action: Callable, set_name: str,
        level: int, show_info: bool = True, **kwargs):
        """SLevel

        Args:
            container (Container): a befogalaló container
            action (Callable): visszatérési metódus
            set_name (str): pályakészlet neve
            level (int): szint száma
        """
        Component.__init__(self, container, **kwargs)

        self.action = action
        self.set_name = set_name
        self.level = level

        if not callable(self.action):
            self.selectable = False

        self.font = config.get_font(config.BUTTON_FONT, config.SMALL_FONT_SIZE)

        self.level_info = loader.jget_info(level, self.set_name)
        assert self.level_info is not None, (f"Hibás set_nam vagy level: "
            f"{set_name}, {level}.")

        self.stats = None
        if show_info:
            self.stats = saves.get_level_statistic(self.set_name, self.level)

        self.size = (228, 400) #TODO padding, margin

        self.color['bg'] = config.BUTTON_DEFAULT_COLOR
        self.color['focus'] = config.BUTTON_FONT_FOCUS_COLOR
        self.color['select'] = config.BUTTON_FONT_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR

        if 'selected' in kwargs and kwargs['selected']:
            self.select = True
        else:
            self.select = False

        space = Space((200,200), None, self.set_name, self.level)
        self.space_image = pg.Surface((200, 200))
        space.draw(self.space_image)

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

        if self.select and self.action is not None:
            self.image.fill(self.color['select'])
        elif self.focus and self.action is not None:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])

        # Pálya képének kirajzolása
        self.image.blit(self.space_image, (14, 14))

        # Név és nehézség
        text = f"{self.level_info['name']} ({self.level_info['dificulty']})"

        rendered = self.font.render(text, True, self.color['font'])
        self.image.blit(rendered, (14, 228))
        
        # Leírás
        lines = self.level_info['description'].split('\n')
        rendered = self.font.render(lines[0], True, self.color['font'])
        self.image.blit(rendered, (14, 288))
        for i in range(1, len(lines)):
            rendered = self.font.render(lines[i], True, self.color['font'])
            self.image.blit(rendered, (14, 288 + i * 30))

        # Ha van róla statisztika akkor a játékos már befejezte a pályát
        # ennek adatai is kirajzoljuk
        if self.stats is not None and self.stats['best_moves'] != 0:
            text = "{:02d}:{:02d}".format(int(self.stats['best_time'] / 60), int(self.stats['best_time'] % 60))
            rendered = self.font.render(text, True, self.color['font'])
            self.image.blit(rendered, (14,14))

            text = str(self.stats['best_moves'])
            rendered = self.font.render(text, True, self.color['font'])
            self.image.blit(rendered, (114 - rendered.get_width(),14))

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