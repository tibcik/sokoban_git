"""Sokoban játék modulja
"""
from __future__ import annotations

import pygame as pg
import time

from utils import Pair
from pygame_menu.utils import EventHandler

from . import config
from .data import loader, saves
from .movepool import MovePool
from .space import Space
from .utils import Statistic
from .objects import *

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController

class Game(pg.sprite.Sprite, EventHandler):
    """Játék

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        set_name (str): pályakészlet neve
        level (int): pálya száma
        space (Space): játéktér
        start_time (float): játék elkezdésének időpontja
        elapsed_time (float): játékkal töltött idő
        run (int): -1|0|1 játék futását jelző flag
        pool (MovePool): játék lépéseit kezelő osztály
        statistic (Statistic): játék statisztikáit megjelenítő osztály
        key_pressed (int): gomb utolsó lenyomásának időpontja
        key_pool (list): lenyomott gombok listája
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

        self.start_time = 0

        self.space = None
        
        self.run = -1
        self.elapsed_time = 0
        self.key_pressed = None
        self.key_pool = []

        self.pool = None
        self.statistic = None

        self.init_level()

    def init_level(self):
        """pálya betöltése
        """
        saves.set_current_level(self.level)

        self.space = Space(self.screen.get_size(), self, self.set_name, self.level)

        self.run = -1
        self.elapsed_time = 0
        self.key_pressed = None
        self.key_pool = []

        self.pool = MovePool(self.space.player)
        self.statistic = Statistic()

    def next_level(self):
        """következő pálya betöltése
        """
        if loader.jget_levels() > (self.level + 1):
            self.level += 1

        self.init_level()

    def restart(self):
        """pálya újrakezdése
        """
        self.init_level()

    def resume(self):
        """visszatérés a játékba
        """
        self.run = 1

    def draw(self, surface: pg.Surface):
        """Játéktár rajzolása

        Args:
            surface (pg.Surface): Felület ahova a játékteret rajzoljuk
        """
        self.space.draw(surface)

        if self.run == 1:
            self.statistic.update(self.elapsed_time, self.pool.current_move)
        statistic_pos = Pair(self.screen.get_size()) - Pair(350,0)
        statistic_pos[1] = 0
        surface.blit(self.statistic.image, statistic_pos)

    def e_KeyDown(self, **kwargs):
        """billentyűzet gombnyomásának lekezelése

        A játék logika itt valósul meg. Sokoban játék logikája:
            - oda lehet lépni ahol nincs semmi akadály
            - ha van ott egy doboz akkor azt el lehet tolni, ha annak irányában nincs akadály
            - ha minden doboz a helyén van a játék véget ér
            - visszalépésnél a karakter és az eltolt dobozok is visszakerülnek az előző pozícióra
            - ha egy gombot nyomva tartunk a karakter gyorsabban kezd el mozogni
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a lenyomott billentyű unicode értéke
            scancode (int?): a lenyomott billenytű scancode értéke"""
        if 'resend' not in kwargs:
            self.key_pool.append(kwargs)
            self.key_pressed = pg.time.get_ticks()

        kwargs = self.key_pool[0]

        key = kwargs['key']

        if key == pg.K_ESCAPE:
            self.key_pool = []
            self.controller.init_game_menu(self, False)
            self.run = False
            return

        if self.space.player.moving:
            return

        move = None
        back = None
        if key == pg.K_UP:
            move = Pair(0, -1)
        elif key == pg.K_DOWN:
            move = Pair(0, 1)
        elif key == pg.K_LEFT:
            move = Pair(-1, 0)
        elif key == pg.K_RIGHT:
            move = Pair(1, 0)
        elif key == pg.K_BACKSPACE:
            back = self.pool.back()
        else:
            return
        
        if move is not None:
            player_pos = self.space.player.pos
            n_player_pos = player_pos + move
            n_box_pos = None
            if self.space[n_player_pos] & loader.SOKOBAN_WALL:
                n_player_pos = None
            elif self.space[n_player_pos] & loader.SOKOBAN_BOX:
                n_box_pos = n_player_pos + move
                if self.space[n_box_pos] & (loader.SOKOBAN_WALL | loader.SOKOBAN_BOX):
                    n_player_pos = None
                    n_box_pos = None

            if n_player_pos is not None:
                if self.run == -1:
                    self.start_time = time.time()
                if self.run < 1:
                    self.run = 1
                self.space.player.move(move)
                self.space[player_pos] -= loader.SOKOBAN_PLAYER
                self.space[n_player_pos] |= loader.SOKOBAN_PLAYER
                self.pool.add(move)
                if n_box_pos is not None:
                    box_obj = pg.sprite.spritecollideany(self.space.player, self.space.boxes)
                    box_obj.move(move)
                    self.space[n_player_pos] -= loader.SOKOBAN_BOX
                    self.space[n_box_pos] |= loader.SOKOBAN_BOX
                    self.pool.add(box_obj)
        elif back is not None:
            n_player_pos = back['player_pos'] + back['move']
            self.space[back['player_pos']] -= loader.SOKOBAN_PLAYER
            self.space[n_player_pos] |= loader.SOKOBAN_PLAYER
            if back['box_pos'] is not None:
                self.space[back['box_pos']] -= loader.SOKOBAN_BOX
                self.space[back['player_pos']] |= loader.SOKOBAN_BOX

        if len(self.key_pool) == 0:
            self.player.fast = False

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        for i in range(len(self.key_pool)):
            if self.key_pool[i]['key'] == kwargs['key']:
                self.key_pool.pop(i)
                self.space.player.fast = False
                break
                
        if self.check_goals():
            self.run = False
            saves.done_level(self.set_name, self.level, self.pool.current_move, self.elapsed_time, True)
            menu = self.controller.init_game_menu(self, True)

    def player_end_move(self):
        """A Player objektum által meghívott metódus mikor a mozgása befejeződik
        """
        if len(self.key_pool) > 0:
            self.e_KeyDown(resend = True)
        else:
            self.space.player.fast = False

    def update(self):
        """Játék frissítése
        """
        if self.run == 1:
            self.elapsed_time = time.time() - self.start_time
            self.statistic.update(self.elapsed_time, self.pool.current_move)

        now = pg.time.get_ticks()
        if len(self.key_pool) > 0 and now - self.key_pressed > 500:
            self.space.player.fast = True

        self.space.objects.update()

    def check_goals(self):
        """Játék befejezésének ellenőrzése"""
        all_in_goal = True
        for box in self.space.boxes:
            if not pg.sprite.spritecollideany(box, self.space.goals):
                all_in_goal = False
                break

        return all_in_goal