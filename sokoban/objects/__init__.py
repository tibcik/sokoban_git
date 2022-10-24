""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: __init__.py
Verzió: 1.0.0
--------------------
sokoban.objects

Sokoban vizuális objektumok

Objektumok:
    SokobanVisualObject
    Empty
    Wall
    Box
    Goal
    Player
    Floor
    Arrow
    Cross

Metódusok:
    resetFramset
"""
from __future__ import annotations

import pygame as pg

from ..utils.frameset import Framesets
from sokoban.data.loader import SOKOBAN_EMPTY, SOKOBAN_WALL, SOKOBAN_FLOOR

from utils import Pair
from sokoban.config import TILE_RESOLUTION

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from sokoban.space import Space
    from sokoban.game import Game

frameset: Framesets = None

def resetFrameset():
    """resetFrameset Kinézet megváltoztatásokat a betöltött képek frissítése
    """
    global frameset

    frameset = None

class SokobanVisualObject(pg.sprite.Sprite):
    """SokobanVisualObject Vizuálsi objektumok ősosztálya

    Arguments:
        pos (Pair): az objetum pozíciója a pályán
        image (pygame.Surface): a megjelenítendő kép
        rect (pygame.rect.Rect + property(getter)): az objetum megjelenítési területe
    """
    def __init__(self, x: int, y: int):
        """SokobanVisualObject

        Args:
            x (int): az objektum vízszintes pozíciója
            y (int): az objektum függőleges pozíciója
        """
        global frameset
        super().__init__()

        self.pos = Pair(x, y)

        self.image = pg.Surface((0, 0), pg.SRCALPHA)

        if frameset is None:
            frameset = Framesets(TILE_RESOLUTION)

    @property
    def rect(self):
        """getter"""
        return pg.rect.Rect(self.pos * TILE_RESOLUTION, TILE_RESOLUTION)

    def draw(self, surface: pg.Surface):
        """draw Objektumot rajzoló metódus

        Args:
            surface (pygame.Surface): A felület ahová az objektumot rajzolni kell_
        """
        surface.blit(self.image, self.rect)
class Empty(SokobanVisualObject):
    """Empty Üres mező
    """
    def __init__(self, x: int, y: int):
        """Empty
        """
        super().__init__(x, y)
        
        if frameset.is_a_frame('empty'):
            _, self.image = frameset.get_frame('empty')
        else:
            self.image = pg.Surface(TILE_RESOLUTION, pg.SRCALPHA)
            self.image.fill((0,0,0,0))

class Wall(SokobanVisualObject):
    """Wall Fal mező
    """
    def __init__(self, x: int, y: int):
        """Wall
        """
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("wall")

    def build(self, space: Space):
        """build Fal típusának meghatározása

        Args:
            space (Space): pálya objektum
        """
        around = ((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))
        wall = ['-' for i in range(8)]
        floor = ['-' for i in range(8)]

        for i in range(8):
            mod = Pair(around[i])
            l_point = self.pos + mod
            try:
                item = space[l_point]
            except:
                item = SOKOBAN_EMPTY

            if item & SOKOBAN_FLOOR:
                floor[i] = '*'
            if (mod.p1 == 0 or mod.p2 == 0) and item & SOKOBAN_WALL:
                wall[i] = '+'
                floor[i] = '+'

        if wall[1] == '-' or wall[3] == '-':
            floor[2] = '?'
        if wall[3] == '-' or wall[5] == '-':
            floor[4] = '?'
        if wall[5] == '-' or wall[7] == '-':
            floor[6] = '?'
        if wall[7] == '-' or wall[1] == '-':
            floor[0] = '?'
        
        floor = "".join(floor)
        tile = f"wall_{floor}"

        try:
            _, self.image = frameset.get_frame(tile)
        except:
            pass

class Box(SokobanVisualObject):
    """Box Doboz mező
    """
    def __init__(self, x: int, y: int):
        """Box
        """
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("box")

    def move(self, way: Pair) -> Box:
        """move Doboz mozgatása

        Args:
            way (Pair): A mozgás iránya

        Returns:
            Box: a mozgás után a visszatérési érték az objektum maga
        """
        self.pos += way

        return self

class Goal(SokobanVisualObject):
    """Goal Végcél mező
    """
    def __init__(self, x: int, y: int):
        """Végcél
        """
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("goal")

class Player(SokobanVisualObject):
    """Player Játékos mező

    Arguments:
        game (Game): Játék objektum
        frame_name (str): Az aktuális játékos kép neve
        was (str): a játékos iránya
        moving (bool): a játékos mozog-e
        move_frame (int): a mozgás aktuális keretszáma
        turning (bool): a játékos fordul-e
        turning_frame (int): a fordulás aktuális keretszáma
        fast (bool): a játékos gyorsan mozog-e
        move_x (float): a játékos x elmozdulásának aránya
        move_y (float): a játékos y elmozdulásának aránya
    """
    def __init__(self, x: int, y: int, game: Game):
        """Player

        Args:
            game (Game): Játék ahol a Player objektum van
        """
        super().__init__(x, y)

        self.game = game
        
        self.frame_name, self.image = frameset.get_frame("idle_down", True)

        self.way = 'down'
        self.moving = False
        self.move_frame = 0
        self.turning = 0
        self.turning_frames = 1
        self.fast = False

        self.move_x = 0
        self.move_y = 0

    def move(self, way: str) -> Player:
        """move Játékos mozgatása

        Args:
            way (str): A mozgás iránya

        Returns:
            Player: az objektum maga
        """
        new_way = 'down'
        if way.p1 > 0:
            new_way = 'right'
        elif way.p1 < 0:
            new_way = 'left'
        elif way.p2 > 0:
            new_way = 'down'
        elif way.p2 < 0:
            new_way = 'up'
        if self.game is not None:
            self.change_way(new_way)
        self.pos += way
        
        return self

    def change_way(self, way: str):
        """change_way Játékos irányválátsa

        Args:
            way (str): új irány neve
        """
        if way != self.way:
            #self.image = frameset.get_frame(f"idle_{way}", 0)
            turn = f"{self.way}_{way}"
            self.way = way

            self.frame_name, self.image = frameset.get_frame(f"turn_{turn}", fast=self.fast)
            self.turn = turn
            self.turning = frameset.get_frame_count(f"turn_{turn}")
            self.turning_frames = self.turning + 1
        else:
            self.frame_name, self.image = frameset.get_frame(f"walk_{way}", reset=True, fast=self.fast)

        self.move_x = TILE_RESOLUTION[0] / frameset.get_frame_count(f"walk_{way}")
        self.move_y = TILE_RESOLUTION[1] / frameset.get_frame_count(f"walk_{way}")
        self.moving = True
        self.move_frame = frameset.get_frame_count(f"walk_{way}")

    @property
    def rect(self):
        """getter"""
        pos = Pair(self.pos) * TILE_RESOLUTION
        if self.way == 'up':
            pos.p2 += self.move_y * self.move_frame
        elif self.way == 'down':
            pos.p2 -= self.move_y * self.move_frame
        elif self.way == 'left':
            pos.p1 += self.move_x * self.move_frame
        elif self.way == 'right':
            pos.p1 -= self.move_x * self.move_frame

        return pg.rect.Rect(pos, self.image.get_size())

    def update(self):
        """update játékos frissítése(animáció)
        """
        next_frame_name, image = frameset.get_frame(self.frame_name, fast=self.fast)
        if image is not None and image != False:
            self.image = image
            if self.frame_name[0:4] == "walk":
                if next_frame_name[0:4] == "idle":
                    self.move_frame = 0
                    self.moving = False
                    self.frame_name = next_frame_name
                    self.game.player_end_move()
                else:
                    self.move_frame -= 1
            else:
                self.frame_name = next_frame_name

class Floor(SokobanVisualObject):
    """Padló mező
    """
    def __init__(self, x: int, y: int):
        """Floor"""
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("floor", 0)

class Arrow(SokobanVisualObject):
    """Nyíl mező"""
    def __init__(self, x: int, y: int, way: str):
        """Arrow

        Args:
            way (str): A nyíl iránya
        """
        super().__init__(x, y)

        self.frame_name, self.image = frameset.get_frame("arrow_up", True)

        self.set_way(way)

    def set_way(self, way: str):
        """set_way A nyíl irányának megváltoztatása

        Args:
            way (str): az irány neve
        """
        new_way = 'down'
        if way == 'r':
            new_way = 'right'
        elif way == 'l':
            new_way = 'left'
        elif way == 'd':
            new_way = 'down'
        elif way == 'u':
            new_way = 'up'

        self.frame_name, self.image = frameset.get_frame(f"arrow_{new_way}", True)

    def update(self):
        """update A nyíl frissítése(animáció)
        """
        self.frame_name, image = frameset.get_frame(self.frame_name)
        if image is not None and image != False:
            self.image = image

class Cross(SokobanVisualObject):
    """Kereszt mező"""
    def __init__(self, x: int, y: int):
        """Cross
        """
        super().__init__(x, y)

        _, self.image = frameset.get_frame("cross")