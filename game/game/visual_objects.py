import pygame as pg
from game.game.frameset import Framesets

from game.game.loader import SOKOBAN_WALL
from game.game.loader import SOKOBAN_FLOOR

from game.pair2 import Pair

frameset = None

import log.log
logger_wall = log.log.init("VisualObject Wall")

class SokobanVisualObject(pg.sprite.Sprite):
    def __init__(self, x, y, game = None):
        global frameset
        super().__init__()

        self.game = game

        self.pos = Pair(x, y)

        self.image = pg.Surface((0, 0), pg.SRCALPHA)

        if frameset is None:
            frameset = Framesets((32, 32))

    @property
    def rect(self):
        return pg.rect.Rect(self.pos * 32, self.image.get_size())

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Empty(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = pg.Surface((32, 32))
        self.image.fill((0,0,0,255))

class Wall(SokobanVisualObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        
        self.image = frameset.get_frame("wall", 0)

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
                continue

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
    
        """
        left = None
        right = None
        up = None
        down = None
        if self.pos.p1 > 0 and space[self.pos.p1 - 1][self.pos.p2] & loader.SOKOBAN_WALL:
            left = 'wall'
        if self.pos.p1 < len(space) - 1 and space[self.pos.p1 + 1][self.pos.p2] & loader.SOKOBAN_WALL:
            right = 'wall'
        if self.pos.p2 > 0 and space[self.pos.p1][self.pos.p2 - 1] & loader.SOKOBAN_WALL:
            up = 'wall'
        if self.pos.p2 < len(space[self.pos.p1]) - 1 and space[self.pos.p1][self.pos.p2 + 1] & loader.SOKOBAN_WALL:
            down = 'wall'

        _up = ''
        _down = ''
        _left = ''
        _right = ''
        upleft = ''
        upright = ''
        downleft = ''
        downright = ''

        if self.pos.p2 > 0 and space[self.pos.p1][self.pos.p2 - 1] & loader.SOKOBAN_FLOOR:
            _up = '_up'
        if self.pos.p2 < len(space[0]) - 1 and space[self.pos.p1][self.pos.p2 + 1] & loader.SOKOBAN_FLOOR:
            _down = '_down'
        if self.pos.p1 > 0 and space[self.pos.p1 - 1][self.pos.p2] & loader.SOKOBAN_FLOOR:
            _left = '_left'
        if self.pos.p1 < len(space) - 1 and space[self.pos.p1 + 1][self.pos.p2] & loader.SOKOBAN_FLOOR:
            _right = '_right'

        if self.pos.p1 > 0 and self.pos.p2 > 0 and space[self.pos.p1 - 1][self.pos.p2 - 1] & loader.SOKOBAN_FLOOR:
            upleft = '_up_left'
        if self.pos.p1 < len(space) - 1 and self.pos.p2 > 0 and space[self.pos.p1 + 1][self.pos.p2 - 1] & loader.SOKOBAN_FLOOR:
            upright = '_up_right'
        if self.pos.p1 > 0 and self.pos.p2 < len(space[0]) - 1 and space[self.pos.p1 - 1][self.pos.p2 + 1] & loader.SOKOBAN_FLOOR:
            downleft = '_down_left'
        if self.pos.p1 < len(space) - 1 and self.pos.p2 < len(space[0]) - 1 and space[self.pos.p1 + 1][self.pos.p2 + 1] & loader.SOKOBAN_FLOOR:
            downright = '_down_right'
        
        if left and right and up and down: #OK
            if upleft and upright and downleft and downright:
                self.image = frameset.get_frame(f"wall_cross_f", 0)
            elif upleft or upright or downleft or downright:
                self.image = frameset.get_frame(f"wall_cross_f{downleft}{downright}{upleft}{upright}", 0)
            else:
                self.image = frameset.get_frame(f"wall_cross", 0)
        elif left and right and up: #OK
            if _down and upleft and upright:
                self.image = frameset.get_frame('wall_cross_up_f', 0)
            elif _down or upleft or upright:
                self.image = frameset.get_frame(f"wall_cross_up_f{_down}{upleft}{upright}", 0)
            else:
                self.image = frameset.get_frame('wall_cross_up', 0)
        elif left and right and down: #OK
            if _up and downleft and downright:
                self.image = frameset.get_frame('wall_cross_down_f', 0)
            elif _up or downleft or downright:
                self.image = frameset.get_frame(f"wall_cross_down_f{downleft}{downright}{_up}", 0)
            else:
                self.image = frameset.get_frame('wall_cross_down', 0)
        elif left and up and down: #OK
            if _right and downleft and upleft:
                self.image = frameset.get_frame('wall_cross_left_f', 0)
            elif _right or downleft or upleft:
                self.image = frameset.get_frame(f"wall_cross_left_f{downleft}{upleft}{_right}", 0)
            else:
                self.image = frameset.get_frame('wall_cross_left', 0)
        elif right and up and down: #OK
            if _left and downright and upright:
                self.image = frameset.get_frame('wall_cross_right_f', 0)
            elif _left or downright or upright:
                self.image = frameset.get_frame(f"wall_cross_right_f{downright}{upright}{_left}", 0)
            else:
                self.image = frameset.get_frame('wall_cross_right', 0)
        elif left and right: #OK
            if _up and _down:
                self.image = frameset.get_frame('wall_horizontal_f', 0)
            elif _up or _down:
                self.image = frameset.get_frame(f"wall_horizontal_f{_down}{_up}", 0)
            else:
                self.image = frameset.get_frame('wall_horizontal', 0)
        elif left and up: #OK
            if upleft and _down:
                self.image = frameset.get_frame('wall_up_left_f', 0)
            elif upleft or _down:
                self.image = frameset.get_frame(f"wall_up_left_f{_down}{upleft}", 0)
            else:
                self.image = frameset.get_frame('wall_up_left', 0)
        elif left and down: #OK
            if downleft and _up:
                self.image = frameset.get_frame('wall_down_left_f', 0)
            elif downleft or _up:
                self.image = frameset.get_frame(f"wall_down_left_f{downleft}{_up}", 0)
            else:
                self.image = frameset.get_frame('wall_down_left', 0)
        elif right and up: #OK
            if upright and _down:
                self.image = frameset.get_frame('wall_up_right_f', 0)
            elif upright or _down:
                self.image = frameset.get_frame(f"wall_up_right_f{_down}{upright}", 0)
            else:
                self.image = frameset.get_frame('wall_up_right', 0)
        elif right and down: #OK
            if downright and _up:
                self.image = frameset.get_frame('wall_down_right_f', 0)
            elif downright or _up:
                self.image = frameset.get_frame(f"wall_down_right_f{downright}{_up}", 0)
            else:
                self.image = frameset.get_frame('wall_down_right', 0)
        elif up and down: #OK
            if _left and _right:
                self.image = frameset.get_frame('wall_vertical_f', 0)
            elif _left or _right:
                self.image = frameset.get_frame(f"wall_vertical_f{_left}{_right}", 0)
            else:
                self.image = frameset.get_frame('wall_vertical', 0)
        elif left: #OK
            if _right:
                self.image = frameset.get_frame('wall_end_right_f', 0)
            else:
                self.image = frameset.get_frame('wall_end_right', 0)
        elif right: #OK
            if _left:
                self.image = frameset.get_frame('wall_end_left_f', 0)
            else:
                self.image = frameset.get_frame('wall_end_left', 0)
        elif up: #OK
            if _down:
                self.image = frameset.get_frame('wall_end_down_f', 0)
            else:
                self.image = frameset.get_frame('wall_end_down', 0)
        elif down: #OK
            if _up:
                self.image = frameset.get_frame('wall_end_up_f', 0)
            else:
                self.image = frameset.get_frame('wall_end_up', 0)"""

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
        super().__init__(x, y, game)
        
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