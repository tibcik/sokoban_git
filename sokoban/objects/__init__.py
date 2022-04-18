import pygame as pg

from ..utils.frameset import Framesets
from sokoban.data.loader import SOKOBAN_EMPTY, SOKOBAN_WALL, SOKOBAN_FLOOR

from utils import Pair
from sokoban.config import TILE_RESOLUTION

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
            self.image = frameset.get_frame('empty', 0)
        else:
            self.image = pg.Surface(TILE_RESOLUTION)
            self.image.fill((0,0,0,255))

class Wall(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = frameset.get_frame("wall", 0)

    def build(self, space):
        circle = ((-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0))
        wall = ['-' for i in range(8)]
        floor = ['-' for i in range(8)]

        if self.pos.p1 == 0 and self.pos.p2 == 1:
            alma = 5

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
            self.image = frameset.get_frame(tile, 0)
        except:
            pass

class Box(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = frameset.get_frame("box", 0)

    def move(self, way):
        self.pos += way

        return self

class Goal(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = frameset.get_frame("goal", 0)

class Player(SokobanVisualObject):
    def __init__(self, x, y, game):
        super().__init__(x, y)

        self.game = game
        
        self.image = frameset.get_frame("idle_down", 0)

        self.way = 'down'
        self.moving = 0
        self.moving_frames = 1
        self.turning = 0
        self.turning_frames = 1
        self.fast = False
        self.last_frame_time = pg.time.get_ticks()

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
        self.change_way(new_way)
        self.pos += way

        return self

    def change_way(self, way):
        if way != self.way:
            #self.image = frameset.get_frame(f"idle_{way}", 0)
            turn = f"{self.way}_{way}"
            self.way = way

            self.image = frameset.get_frame(f"turn_{turn}", 0)
            self.turn = turn
            self.turning = frameset.get_frame_count(f"turn_{turn}")
            self.turning_frames = self.turning + 1
        else:
            self.image = frameset.get_frame(f"walk_{way}", 0)
        self.moving = frameset.get_frame_count(f"walk_{way}")
        self.moving_frames = self.moving + 1

    @property
    def rect(self):
        pos = Pair(self.pos) * 32
        if self.way == 'up':
            pos.p2 += 32 * (self.moving / self.moving_frames)
        elif self.way == 'down':
            pos.p2 -= 32 * (self.moving / self.moving_frames)
        elif self.way == 'left':
            pos.p1 += 32 * (self.moving / self.moving_frames)
        elif self.way == 'right':
            pos.p1 -= 32 * (self.moving / self.moving_frames)
        return pg.rect.Rect(pos, self.image.get_size())

    def update(self):
        if self.turning > 0:
            now = pg.time.get_ticks()
            if now - self.last_frame_time > (50 if self.fast else 200) / (self.turning_frames + self.moving_frames - 2):
                self.last_frame_time = now
                self.image = frameset.get_next_frame(f"turn_{self.turn}")
                self.turning -= 1
                if self.turning == 0:
                    self.image = frameset.get_frame(f"walk_{self.way}", 0)
        elif self.moving > 0:
            now = pg.time.get_ticks()
            if now - self.last_frame_time > (50 if self.fast else 200) / (self.turning_frames + self.moving_frames - 2):
                self.last_frame_time = now
                self.image = frameset.get_next_frame(f"walk_{self.way}")
                self.moving -= 1
                if self.moving == 0:
                    self.game.player_end_move()
        else:
            now = pg.time.get_ticks()
            if now - self.last_frame_time > 2000:
                self.last_frame_time = now - 1800
                self.image = frameset.get_next_frame(f"idle_{self.way}")

class Floor(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = frameset.get_frame("floor", 0)