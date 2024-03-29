""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: select.py
Verzió: 1.0.0
--------------------
pygame_menu.components.select

Elemválasztó menüelem

Osztályok:
    Select
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *
from utils import Pair, betweens

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class Select(KeyboardGrabber, Scrollable, MouseGrabber, Selectable, Component):
    """Select osztály.

    Container osztályban felhasználható select menüelem. Az elem bal és jobb
    oldalára kattintva lehet választani az előre beállított elem közül.
    
    Attributes:
        selected (int): a kiválasztott elem indexe
        animation (dict): az elem értékének megváltoztatásokor lezajlódó animációhoz {'run': bool, 'tick': int, 'way': int}
        items(property) (tuple[str]): a választható elemek
        font(property) (pygame.font.Font): a gomb betűtipusa
        value(property csak getter) (str): a kiválasztott elem értékét adja vissza"""
    def __init__(self, container: Container, items: tuple(str), selected: int = 0, font_size: int = config.DEFAULT_FONT_SIZE, **kwargs):
        """belépési pont
        
        Args:
            container (Container): a befogalaló container
            items (tuple[str]): a kiválasztható elemek
            selected (int): az előre kivcálasztott elem. Defaults to 0.
            font_size (int): a szöveg mérete. Defaults to config.DEFAULT_FONT_SIZE.
        
        Kwargs:
            -> Component.__init__(...)"""
        Component.__init__(self, container, **kwargs)

        self.items = items
        self.font = config.get_font(config.SELECT_FONT, config.DEFAULT_FONT_SIZE)

        self.selected = betweens(selected, 0, len(self.items) - 1)

        self.animate = {'run': False, 'tick': 0, 'way': 0}

        self.color['bg'] = config.SELECT_DEFAULT_COLOR
        self.color['focus'] = config.SELECT_FOCUS_COLOR
        self.color['select'] = config.SELECT_SELECT_COLOR
        self.color['arrow'] = config.SELECT_ARROW_COLOR
        self.color['font'] = config.SELECT_FONT_COLOR

        # Az előre kiválasztott elem megjelenítése
        self.update_image()
        self.scroll = {'x': self.size[0] * self.selected}

    @property
    def items(self) -> tuple(str):
        """getter"""
        return self._items

    @items.setter
    def items(self, value: tuple(str)):
        """setter
        
        Raises:
            ValueError: Ha nem listaszerű"""
        ex.arg_attribute_exception('value', value, '__getitem__')
        
        # Az üres strigek kihagyása
        self._items = [str(item) for item in value if len(str(item)) > 0]
        # Ha a régi méret egyenlő a kép méretével akkor nincs előre beállított
        # méret. Az új méret a kép mérete lesz.
        if self.size == (0, 0) or self.size == Pair(self.image.get_size()):
            # A font inicializálása után
            if hasattr(self, "_font"):
                # TODO: több item
                width = 0
                iwidth = None
                for item in self.items:
                    iwidth = self.font.size(item)
                    width = iwidth[0] if width < iwidth[0] else width
                self.size = Pair(width, iwidth[1]) + Pair(10,10)

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
        self.items = self._items

    @property
    def value(self) -> str:
        """getter"""
        return self.items[self.selected]

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface((self.size.p1 * len(self.items), self.size.p2), pg.SRCALPHA)

        color = self.color['bg']
        if self.select:
            color = self.color['select']
        elif self.focus:
            color = self.color['focus']

        self.image.fill(color)

        # Elemek kirajzolása, minden elem egy select méretű részre kerül kirajzolásra
        for i in range(len(self.items)):
            item = self.items[i]
            rendered = self.font.render(item, True, self.color['font'])
            pos = self.size / 2 - Pair(rendered.get_size()) / 2 + self.size * i
            pos[1] = 8

            self.image.blit(rendered, pos)

        # Ha kell akkor kirajzoljuk a nyilakat
        # TODO: ezt a rész nem javítottam eddig ki, majd ha meg lesz a játék
        # TODO: teljes kinézete ez is kijavításra fog kerülni...
        if self.focus and not self.animate['run']:
            arrow = pg.Surface((6,26), pg.SRCALPHA)
            pg.draw.polygon(arrow, self.color['arrow'], ((0,13),(6,0),(6,26))) # TODO ide képet kell tenni...
            self.image.blit(arrow, (2 + self.size[0] * self.selected,3))
            arrow = pg.Surface((6,26), pg.SRCALPHA)
            pg.draw.polygon(arrow, self.color['arrow'], ((6,13),(0,0),(0,26))) # TODO ide képet kell tenni...
            self.image.blit(arrow, (self.size[0] - 8 + self.size[0] * self.selected,3))

    def update(self):
        """frissítés
        
        Animáció az elemváltoztatásnál."""
        if self.animate['run']:
            now = pg.time.get_ticks()
            if now - self.animate['tick'] > 10:
                self.scroll = {'relx': self.animate['way'] * 5}

                # Ha a scrollozás túlhalad volna azon a ponton ahol álnia kéne
                # beállítjuk a helyes értékre és leállítjuk az animációt
                check = "__le__" if self.animate['way'] < 0 else "__ge__"
                if getattr(self.scroll[0], check)(self.size[0] * self.selected):
                    self.scroll = {'x': self.size[0] * self.selected}
                    self.animate = {'run': False, 'tick': 0, 'way': 0}
                    self.updated()

                self.animate['tick'] = now
                self.container.updated()
        
    def e_MouseButtonUp(self, pos, **kwargs):
        """egér gombelengedés kezelése
        
        Args:
            pos (tuple): az mutató pozíciója

        Kwargs:
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        # TODO: ezt lehet érdemes lenne átírni, ha kiderül mekkora lesz a nyíl
        if pos[0] < self.size[0] * 0.2:
            self.e_KeyUp(pg.K_LEFT)
        elif pos[0] > self.size[0] * 0.8:
            self.e_KeyUp(pg.K_RIGHT)

    def e_KeyDown(self, key, **kwargs):
        """billentyűzet gombnyomásának lekezelése

        Args:
            key (int): a billentyű kódja
        
        Kwargs:
            mod (int): módosítóbillentyűk
            unicode (char): a lenyomott billentyű unicode értéke
            scancode (int?): a lenyomott billenytű scancode értéke"""
        if key == pg.K_LEFT or key == pg.K_RIGHT:
            self.grab_keyboard()
        else:
            self.release_keyboard()

    def e_KeyUp(self, key, **kwargs):
        """billentyűzet gombfelengedésének lekezelése

        Args:
            key (int): a billentyű kódja
        
        Kwargs:
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        if key == pg.K_LEFT:
            if (self.selected - 1) >= 0:
                self.selected -= 1
                self.animate = {'run': True, 'tick': pg.time.get_ticks(), 'way': -1}
        elif key == pg.K_RIGHT:
            if (self.selected + 1) < len(self.items):
                self.selected += 1
                self.animate = {'run': True, 'tick': pg.time.get_ticks(), 'way': 1}

        self.updated()
