"""Set választó osztály modulja

Nem tisztán menüelem, mivel a működéséhez szükséges a sokoban játék néhány osztálya.
"""
from __future__ import annotations

import pygame as pg
from datetime import datetime

import config #TODO: refactiring
import game.game.loader as loader #TODO: refactoring
from game.game.space import Space #TODO: refactoring
import config.saves as save #TODO: refactoring

from ..components.component import *
from utils import Pair

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Callable

class SSet(MouseGrabber, Selectable, Component):
    """SSet osztály.

    Container osztályban felhasználható szet adatai kijelző menüelem. Lehet 
    választható.
    
    Attributes:
        action: callable a kiválasztáskor lefuttadandó metódus
        set_name: str a set ahonnan a szint van
        set_info: dict a szet adatai: név, nehézség, leírás, pályák száma
        stats: dict a játékos teljesítménye ezen a szinten
        levels_image: pygame.Surface a pályák képe
        font(property): pg.font.Font a gomb betűtipusa"""
    def __init__(self, container: Container, action: Callable, set_name: str,
        **kwargs):
        """belépési pont
        
        Args:
            container: a befogalaló container
            action: kiválasztás esetén futtatandó metódus
            set_name: a set neve
            kwargs: {position, size, sticky}"""
        Component.__init__(self, container, **kwargs)

        assert callable(action), f"Vár calabble típus, kapott {type(action)}"
        self.action = action
        self.set_name = set_name

        self.font = config.get_font(config.BUTTON_FONT, config.DEFAULT_FONT_SIZE)

        self.set_info = loader.jget_info(None, self.set_name)
        assert self.set_info is not None, (f"Hibás set_nam vagy level: "
            f"{set_name}.")

        self.stats = save.get_set_statistic(self.set_name)

        self.size = (228, 500) #TODO padding, margin

        self.color['bg'] = config.BUTTON_DEFAULT_COLOR
        self.color['focus'] = config.BUTTON_FOCUS_COLOR
        self.color['select'] = config.BUTTON_SELECT_COLOR
        self.color['font'] = config.BUTTON_FONT_COLOR

        if 'selected' in kwargs and kwargs['selected']:
            self.select = True
        else:
            self.select = False

        self.levels_image = pg.Surface((200,300))
        self.make_levels_image()

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

    def make_levels_image(self):
        """Az első öt pálya képét rajzolja ki"""
        for level in range(min(loader.jget_levels()-1,4),-1,-1):
            space = Space(None, self.set_name, level, (200-10*level,200-20*level))
            space.draw(self.levels_image, Pair(0,0)+Pair(5,40)*level,
                'd' if level != 0 else 'c') # TODO: space rafactoring...
            pos = Pair(0,0)+Pair(5,40)*level
            size = (200-10*level-2,200-20*level)
            pg.draw.lines(self.levels_image, (255,0,0), True,
                (pos,(pos+Pair(size[0], 0)),pos+Pair(size),(pos+Pair(0,size[1]))), 2)

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
        self.image.blit(self.levels_image, (14, 14))

        # Név és nehézség
        text = f"{self.set_info['name']} ({self.set_info['dificulty']})"
        rendered = self.font.render(text, True, self.color['font'])
        self.image.blit(rendered, (14, 328))

        # Pályák száma a set-ben és az ezekből elvégzettek száma
        done_levels = self.stats['done_levels'] if self.stats else 0
        text = f"Pályák: {done_levels}/{loader.jget_levels()}"
        rendered = self.font.render(text, True, self.color['font'])
        self.image.blit(rendered, (14, 368))
        
        # Leírás
        lines = self.set_info['description'].split('\n')
        rendered = self.font.render(lines[0], True, self.color['font'])
        self.image.blit(rendered, (14, 408))
        for i in range(1, len(lines)):
            rendered = self.font.render(lines[i], True, self.color['font'])
            self.image.blit(rendered, (14, 408 + i * 30))

    def e_MouseButtonUp(self, **kwargs):
        """egér mozgás kezelése
        
        Args:
            kwargs: {pos, rel, button, touch}"""
        if callable(self.action):
            self.action(self)

    def e_KeyUp(self, key, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Args:
            key: ...
            kwargs: {mod, unicode, scancode}"""
        if key in (pg.K_RETURN, pg.K_KP_ENTER) and callable(self.action):
            self.action(self)