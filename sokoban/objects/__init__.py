from math import floor
import pygame as pg

import time

from ..utils.frameset2 import Framesets
from sokoban.data.loader import SOKOBAN_EMPTY, SOKOBAN_WALL, SOKOBAN_FLOOR

from utils import Pair
from sokoban.config import TILE_RESOLUTION, SPACE_BG_COLOR

frameset: Framesets = None

class SokobanVisualObject(pg.sprite.Sprite):
    def __init__(self, x, y):
        global frameset
        super().__init__()

        self.pos = Pair(x, y)

        self.image = pg.Surface((0, 0), pg.SRCALPHA)

        if frameset is None:
            frameset = Framesets(TILE_RESOLUTION)

    @property
    def rect(self):
        return pg.rect.Rect(self.pos * TILE_RESOLUTION, TILE_RESOLUTION)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
class Empty(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        if frameset.is_a_frame('empty'):
            _, self.image = frameset.get_frame('empty')
        else:
            self.image = pg.Surface(TILE_RESOLUTION)
            self.image.fill(SPACE_BG_COLOR)

class Wall(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("wall")

    def build(self, space):
        circle = ((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))
        wall = ['-' for i in range(8)]
        floor = ['-' for i in range(8)]

        for i in range(8):
            mod = Pair(circle[i])
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

    def build2(self, space):
        circle = ((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))
        wall = ['-' for i in range(8)]
        floor = ['-' for i in range(8)]

        for i in range(8):
            mod = Pair(circle[i])
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

        self.image = pg.Surface(TILE_RESOLUTION, pg.SRCALPHA)

        empty = Empty(0,0)
        self.image.blit(empty.image, (0, 0))
        _, floor_img = frameset.get_frame("floor")

        pos = Pair(TILE_RESOLUTION)
        hx = int(TILE_RESOLUTION[0] / 2)
        hy = int(TILE_RESOLUTION[1] / 2)

        if floor[0] == '*':
            self.image.blit(floor_img, (0,0), (0,0,hx,hy)) 
        if floor[2] == '*':
            self.image.blit(floor_img, (hx,0), (hx,0,hx,hy))
        if floor[4] == '*':
            self.image.blit(floor_img, (hx,hx), (hx,hy,hx,hy))
        if floor[6] == '*':
            self.image.blit(floor_img, (0,hy), (0,hy,hx,hy))

        for i in range(len(floor)):
            if floor[i] == '*':
                floor[i] = '-'

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
            _, wall_img = frameset.get_frame(tile)
            #print(tile)
        except:
            _, wall_img = frameset.get_frame('wall')

        self.image.blit(wall_img, (0,0))

class Box(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("box")

    def move(self, way):
        self.pos += way

        return self

class Goal(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("goal")

class Player(SokobanVisualObject):
    def __init__(self, x, y, game):
        super().__init__(x, y)

        self.game = game
        
        self.frame_name, self.image = frameset.get_frame("idle_down", True)

        self.way = 'down'
        self.moving = False
        self.move_frame = 0
        self.turning = 0
        self.turning_frames = 1
        self.fast = False
        self.last_frame_time = time.time()

        self.move_x = 0
        self.move_y = 0

    def move(self, way):
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

    def change_way(self, way):
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

        self.last_frame_time = time.time()

    @property
    def rect(self):
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
    def __init__(self, x, y):
        super().__init__(x, y)
        
        _, self.image = frameset.get_frame("floor", 0)

class Arrow(SokobanVisualObject):
    def __init__(self, x, y, way):
        super().__init__(x, y)

        self.frame_name, self.image = frameset.get_frame("arrow_up", True)

        self.set_way(way)

    def set_way(self, way):
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
        self.frame_name, image = frameset.get_frame(self.frame_name)
        if image is not None and image != False:
            self.image = image

class Cross(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)

        _, self.image = frameset.get_frame("cross")