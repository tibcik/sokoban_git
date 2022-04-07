import copy

import pygame as pg
import numpy as np

from game.game.visual_objects import *
from game.pair2 import Pair
import game.game.loader as loader

import log.log
logger = log.log.init("Game")

visual_space_types = {
#    loader.SOKOBAN_EMPTY: {'obj': Empty, 'var': 'emptys'},
    loader.SOKOBAN_FLOOR: {'obj': Floor, 'var': 'floors'},
    loader.SOKOBAN_WALL: {'obj': Wall, 'var': 'walls'},
    loader.SOKOBAN_GOAL: {'obj': Goal, 'var': 'goals'},
    loader.SOKOBAN_BOX: {'obj': Box, 'var': 'boxes'},
    loader.SOKOBAN_PLAYER: {'obj': Player, 'var': None}
}

class Space(pg.sprite.Sprite):
    def __init__(self, game, set_name, level, space_size):
        self.game = game
        self.set_name = set_name
        self.level = level

        self.space_size = Pair(space_size)
        self.size = Pair(0,0)
        self.scale = 1
        self.offset = Pair(0,0)
        self.raw = None

        self.objects = pg.sprite.Group()
        self.emptys = pg.sprite.Group()
        self.floors = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.boxes = pg.sprite.Group()
        self.player = None

        self.editor = False

        if self.level is not None:
            self.init_level()

    def init_level(self):
        data = loader.jget_data(self.level, self.set_name)
        self.init_level_data(data)

    def init_level_data(self, data):
        self.scale = 0

        self.raw = data

        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                for t in visual_space_types:
                    if t & data[y,x]:
                        if visual_space_types[t]['var'] is None and t == loader.SOKOBAN_PLAYER:
                            self.player = Player(x, y, self.game)
                        elif visual_space_types[t]['var'] is not None:
                            getattr(self, visual_space_types[t]['var']).add(visual_space_types[t]['obj'](x, y))

        self.size = Pair(data.shape[1], data.shape[0])

        self.objects.add(self.emptys)
        self.objects.add(self.floors)
        self.objects.add(self.walls)
        self.objects.add(self.goals)
        self.objects.add(self.boxes)
        if self.player:
            self.objects.add(self.player)

        for wall in self.walls:
            wall.build(self)

        canvas_size = self.size * 32
        screen_size = self.space_size

        self.offset = screen_size * 0.5

        x_rate, y_rate = screen_size.p1 / canvas_size.p1, screen_size.p2 / canvas_size.p2
        rate = min(x_rate, y_rate)
        self.scale = rate

    def __getitem__(self, i):
        if hasattr(i, '__getitem__') and len(i) == 2:
            x = i[0]
            y = i[1]

            return self.raw[y,x]
        
        return None

    def __setitem__(self, i, value):
        if not hasattr(i, '__getitem__') or len(i) < 2:
            return
        
        x = i[0]
        y = i[1]

        self.raw[y,x] = value

        if self.editor:
            empty = Empty(x, y)
            pg.sprite.spritecollide(empty, self.objects, True)
            for t in visual_space_types:
                if t & value:
                    if t == loader.SOKOBAN_PLAYER:
                        v_obj = visual_space_types[t]['obj'](x, y, self.game)
                    else:
                        v_obj = visual_space_types[t]['obj'](x, y)
                        getattr(self, visual_space_types[t]['var']).add(v_obj)
                    self.objects.add(v_obj)

            for wall in self.walls:
                wall.build(self)

    def recalc_size(self):
        canvas_size = self.size * 32
        screen_size = self.space_size

        self.offset = screen_size * 0.5

        x_rate, y_rate = screen_size.p1 / canvas_size.p1, screen_size.p2 / canvas_size.p2
        rate = min(x_rate, y_rate)
        self.scale = rate

    def add_row(self):
        cols = self.raw.shape[1]
        self.raw = np.r_[self.raw, np.ones((1,cols), np.byte)]
        self.size.p2 += 1
        self.recalc_size()

    def add_column(self):
        rows = self.raw.shape[0]
        self.raw = np.c_[self.raw, np.ones(rows, np.byte)]
        self.size.p1 += 1
        self.recalc_size()

    def remove_row(self):
        if self.raw.shape[0] == 3:
            return
        self.raw = self.raw[:-1]
        self.size.p2 -= 1
        self.recalc_size()

    def remove_column(self):
        if self.raw.shape[1] == 3:
            return
        self.raw = self.raw[:,:-1]
        self.size.p1 -= 1
        self.recalc_size()

    def is_row_empty(self, row):
        return np.all(np.equal(self.raw[row], loader.SOKOBAN_EMPTY))

    def is_column_empty(self, column):
        return np.all(np.equal(self.raw[:,column], loader.SOKOBAN_EMPTY))

    def check(self):
        # Körben lennie kell egy 1 vastag üres résznek, ha nincs javítandó
        rows = self.raw.shape[0]
        cols = self.raw.shape[1]
        if not self.is_row_empty(0):
            self.raw = np.r_[np.ones((1, cols), np.byte), self.raw]
            self.size.p2 += 1
            rows += 1
        if not self.is_row_empty(rows - 1):
            self.raw = np.r_[self.raw, np.ones((1, cols), np.byte)]
            self.size.p2 += 1
            rows += 1
        if not self.is_column_empty(0):
            self.raw = np.c_[np.ones((cols, 1), np.byte), self.raw]
            self.size.p1 += 1
            cols += 1
        if not self.is_column_empty(cols - 1):
            self.raw = np.c_[self.raw, np.ones((cols, 1), np.byte)]
            self.size.p1 += 1
            cols += 1
        self.recalc_size()

    def draw(self, surface, pos = (0,0), sticky = 'c', grid = False):
        bg = pg.Surface(self.space_size)
        bg.fill((0,200,150)) #TODO: skinből...
        canvas = pg.Surface(self.size * 32, pg.SRCALPHA)
        for obj in self.objects:
            obj.draw(canvas)
        
        if grid:
            for y in range(self.raw.shape[0]):
                for x in range(self.raw.shape[1]):
                    pg.draw.rect(canvas, (150,150,150), (x*32,y*32,32,32), 1)

        if self.scale != 1:
            canvas = pg.transform.scale(canvas, self.size * self.scale * 32)

        rect = canvas.get_rect()
        if sticky == 'd':
            rect.centerx = self.offset.p1
            rect.bottom = self.space_size.p2
        else:
            rect.center = self.offset
        bg.blit(canvas, rect)
        surface.blit(bg, pos)

    def rect(self):
        return self.image.get_size()
