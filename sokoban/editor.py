""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: editor.py
Verzió: 1.0.0
--------------------
sokoban.editor

Pályaszerkesztő

Osztályok:
    Editor
"""
from __future__ import annotations
from math import floor
#from attr import has

import pygame as pg
import time

from utils import Pair, between
from pygame_menu.utils import EventHandler

from . import config
from .data import loader, saves
from .movepool import MovePool
from .editor_space import Space
from .utils import Statistic
from .objects import *

from sokoban import solver

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class Editor(pg.sprite.Sprite, EventHandler):
    """Pályaszerkesztő

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        set_name (str): pályakészlet neve
        level (int): pálya száma
        focused (Pair): az éppen fókusz alatt lévő mező
        selected (Pair): a kiválasztott mező
        space (Space): játéktér
        selected_tool (int): a kiválasztott mező típusa
        image (pygame.Surface): a statikus háttérkép
        dinimage (pygame.Surface): a kép dinamikus része
    """
    def __init__(self, controller: MainController, screen: pg.Surface, set_name: str, level: int):
        """Game

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pg.Surface): teljes megjelenítési felület
            set_name (str): pályakészlet neve
            level (int): pálya száma
        """
        pg.sprite.Sprite.__init__(self)

        self.controller = controller
        self.screen = screen

        self.set_name = set_name
        self.level = level

        self.focused = Pair(0,0)
        self.selected = Pair(0,0)

        self.space = Space(Pair(self.screen.get_size()) - Pair(240,0), None, self.set_name, self.level)

        self.selected_tool = 0

        self.image = None
        self.dinimage = None
        self.init_image()

    def init_image(self):
        """init_image Statikus háttér betöltése
        """
        self.image = pg.Surface((240,self.screen.get_size()[1]), pg.SRCALPHA)

        obj = Empty(0.5,1)
        obj.draw(self.image)
        obj = Wall(0.5,2.5)
        obj.draw(self.image)
        obj = Floor(0.5,4)
        obj.draw(self.image)
        obj = Floor(0.5,5.5)
        obj.draw(self.image)
        obj = Goal(0.5,5.5)
        obj.draw(self.image)
        obj = Box(0.5,7)
        obj.draw(self.image)
        obj = Player(0.5,8.5, None)
        obj.draw(self.image)

        self.font = config.get_font(config.LABEL_FONT, config.DEFAULT_FONT_SIZE)

        rendered = self.font.render("Üres terület(1)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,32))
        rendered = self.font.render("Fal(2)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,80))
        rendered = self.font.render("Padló(3)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,128))
        rendered = self.font.render("Cél(4)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,176))
        rendered = self.font.render("Láda(5)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,226))
        rendered = self.font.render("Játékos(6)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (52,274))

        rendered = self.font.render("Menü(m)", True, config.LABEL_FONT_COLOR)
        self.image.blit(rendered, (16,self.screen.get_size()[1] - 60))

    def update_image(self):
        """update_image Dinamikus háttér frissítése
        """
        self.dinimage = pg.Surface((240,self.screen.get_size()[1]), pg.SRCALPHA)

        selected_pos_y = self.selected_tool * 48 + 32
        pg.draw.rect(self.dinimage, (255,150,150), (16,selected_pos_y,TILE_RESOLUTION[0],TILE_RESOLUTION[1]), 3)

    def draw(self, surface: pg.Surface):
        """Játéktár rajzolása

        Args:
            surface (pg.Surface): Felület ahova a játékteret rajzoljuk
        """
        self.space.draw(surface, (240,0))

        self.update_image()
        surface.blit(self.image, (0,0))
        surface.blit(self.dinimage, (0,0))

    def e_MouseButtonDown(self, pos: tuple, button: int, **kwargs):
        """e_MouseButtonDown Egér gombnyomás lekezelése

        Args:
            pos (pos): a mutató pozíciója
            button (button): a lenyomott gomb azonosítója
        """
        mpos = pos
        rmpos = Pair(pos)
        rmpos -= Pair(240,0)

        csize = self.space.size * TILE_RESOLUTION
        csize *= self.space.scale
        rmpos -= (Pair(self.screen.get_size()) - Pair(240,0) - csize) / 2

        pos = rmpos / (Pair(TILE_RESOLUTION) * self.space.scale)

        if not between(pos.p1, 0, self.space.size[0]):
            pos.p1 = -1
            pos.p2 = -1
        if not between(pos.p2, 0, self.space.size[1]):
            pos.p1 = -1
            pos.p2 = -1

        if button == 1 and pos != (-1,-1):
            pos = Pair(pos[0], pos[1])
            self.space.selected = pos
            self.e_KeyDown(pg.K_RETURN)
        else:
            if not between(mpos[0], 16, 230):
                return
            if not between(mpos[1], 14, 314):
                return

            self.selected_tool = floor((mpos[1] - 14) / 50)

    def e_MouseMotion(self, pos: tuple, rel: tuple, buttons: tuple, **kwargs):
        """e_MouseMotion Egér eszköz mozgatásának lekezelése

        Args:
            pos (tuple): a mutató pozíciója
            rel (tuple): a mutató relatív pozíciója
            buttons (tuple): a lenyomott egérgombok
        """
        rmpos = Pair(pos)
        rmpos -= Pair(240,0)

        csize = self.space.size * TILE_RESOLUTION
        csize *= self.space.scale
        rmpos -= (Pair(self.screen.get_size()) - Pair(240,0) - csize) / 2

        pos = rmpos / (Pair(TILE_RESOLUTION) * self.space.scale)

        if not between(pos.p1, 0, self.space.size[0]):
            pos.p1 = -1
            pos.p2 = -1
        if not between(pos.p2, 0, self.space.size[1]):
            pos.p1 = -1
            pos.p2 = -1

        if buttons[0] and pos != (-1,-1):
            pos = Pair(pos[0], pos[1])
            self.space.selected = pos
            self.e_KeyDown(pg.K_RETURN)

    def e_KeyDown(self, key: tuple, **kwargs):
        """e_KeyDown egérgomb felengedésének lekezelése

        Args:
            key (tuple): a felengedett gomb azonosítója
        """
        numkeys = (pg.K_1,pg.K_2,pg.K_3,pg.K_4,pg.K_5,pg.K_6)
        tools = (loader.SOKOBAN_EMPTY, loader.SOKOBAN_WALL, loader.SOKOBAN_FLOOR,
            loader.SOKOBAN_GOAL | loader.SOKOBAN_FLOOR, loader.SOKOBAN_BOX | loader.SOKOBAN_FLOOR,
            loader.SOKOBAN_PLAYER | loader.SOKOBAN_FLOOR)

        if key == pg.K_UP:
            if self.space.selected.p2 != 0:
                self.space.selected.p2 -= 1
        elif key == pg.K_DOWN:
            if self.space.selected.p2 != self.space.size.p2 - 1:
                self.space.selected.p2 += 1
        elif key == pg.K_LEFT:
            if self.space.selected.p1 != 0:
                self.space.selected.p1 -= 1
        elif key == pg.K_RIGHT:
            if self.space.selected.p1 != self.space.size.p1 - 1:
                self.space.selected.p1 += 1
        elif key in numkeys:
            self.selected_tool = numkeys.index(key)
        elif key == pg.K_RETURN:
            tool = tools[self.selected_tool]
            if self.space[self.space.selected] & loader.SOKOBAN_GOAL:
                if tools[self.selected_tool] & loader.SOKOBAN_BOX or tools[self.selected_tool] & loader.SOKOBAN_PLAYER:
                    tool |= loader.SOKOBAN_GOAL
            if self.space[self.space.selected] & loader.SOKOBAN_PLAYER:
                self.space.player = None
            if tools[self.selected_tool] & loader.SOKOBAN_PLAYER:
                if self.space.player is not None and self.space[self.space.player.pos] & loader.SOKOBAN_GOAL:
                    self.space.raw[self.space.raw >= loader.SOKOBAN_PLAYER] = loader.SOKOBAN_FLOOR | loader.SOKOBAN_GOAL
                else:
                    self.space.raw[self.space.raw >= loader.SOKOBAN_PLAYER] = loader.SOKOBAN_FLOOR
            self.space[self.space.selected] = tool
        elif key == pg.K_m or key == pg.K_ESCAPE:
            self.controller.init_editor_menu(self)

    def update(self):
        pass

    def validate(self):
        pass