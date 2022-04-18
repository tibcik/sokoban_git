"""Játéktér modulja

A Space osztály a játéktár megjelenítéséért felel, használható bárhol ahol
meg szeretnénk jeleníteni egy pályát.
"""
from __future__ import annotations

import pygame as pg
import numpy as np

from .objects import *
from utils import Pair
from .data import loader
from .config import TILE_RESOLUTION, SPACE_BG_COLOR

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game import Game

# A pálya felépítéséhez szükséges objektum
visual_space_types = {
    loader.SOKOBAN_EMPTY: {'obj': Empty, 'var': 'empties'},
    loader.SOKOBAN_FLOOR: {'obj': Floor, 'var': 'floors'},
    loader.SOKOBAN_WALL: {'obj': Wall, 'var': 'walls'},
    loader.SOKOBAN_GOAL: {'obj': Goal, 'var': 'goals'},
    loader.SOKOBAN_BOX: {'obj': Box, 'var': 'boxes'},
    loader.SOKOBAN_PLAYER: {'obj': Player, 'var': None}
}

class Space(pg.sprite.Sprite):
    """Space osztály.

    Ez az osztály felel a játéktér megjelenítéséért. Főként a Game osztály
    használja, de bárhonnan máshonbnan is meghívható ahol szükség van a szint
    megjelenítésére.
    
    Attributes:
        game: Game|None a játéknak fenntartva
        set_name: str|None a pályakészlet neve
        level: int|None a pálya száma a pályakészletben
        space_size: Pair a játéktér megjelnítésére lévő kép mérete
        size: Pair a játéktér tényleges mérete
        scale: floot a megjelenítésre szükséges hely és a tényleges hely arányszáma
        offset: Pair x, y eltolás értéke(pl.: a pálya közepré igazítása érdekében)
        raw: NumpyArray a pálya aktuális állását replezentáló két dimenziós tömb
        editor: bool kapcsoló ami jelzi, hogy az objektumot a játékon vagy a szerkesztőn
            belül használjuk-e

        empties: pygame.sprite.Group a játéktéren kívüli csempék gyűjteménye
        floors: pygame.sprite.Group a játéktéren belüli csempék(padló) gyűjteménye
        walls: pygame.sprite.Group a fal csempék gyűjteménye
        goals: pygame.sprite.Group a dobozok végső helyeinek gyűjteménye
        boxes: pygame.sprite.Group a dobozok gyűjteménye
        player: sokoban.objects.Player a karakter objektuma"""
    def __init__(self, space_size: Pair, game: Game = None, set_name: str = None,
        level: int = None):
        """belépési pont
        
        Args:
            space_size: a játéktér megjelnítésére lévő kép mérete
            game: a játéknak fenntartva,
            set_name: a pályakészlet neve
            level: a pálya száma a pályakészletben"""
        self.game = game
        self.set_name = set_name
        self.level = level

        self.space_size = Pair(space_size)
        self.size = Pair(0,0)
        self.scale = 1
        self.offset = Pair(0,0)
        self.raw = None

        self.objects = pg.sprite.Group()
        self.empties = pg.sprite.Group()
        self.floors = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        self.boxes = pg.sprite.Group()
        self.player = None

        self.editor = False

        if self.level is not None:
            self.init_level()

    def init_level(self):
        """Meglévő pálya betöltése
        """
        assert self.set_name in loader.jget_sets(), (f"A \"{self.set_name}\" nem"
            "egy létező pályakészlet!")
        assert self.level < loader.jget_levels(self.set_name), (f"A {self.level}. "
            f" pálya nem része a {self.set_name} pályakészletnek!")

        data = loader.jget_data(self.level, self.set_name)
        self.init_level_data(data)

    def init_level_data(self, data):
        """Pálya betöltése
        
        Args:
            data: NumpyArray a pálya aktuális állását replezentáló két dimenziós tömb"""
        self.scale = 0

        self.raw = data

        # Pálya vizuális objektumainek létrehozása
        for y in range(data.shape[0]):
            for x in range(data.shape[1]):
                for t in visual_space_types:
                    if t & data[y,x]:
                        if visual_space_types[t]['var'] is None and t == loader.SOKOBAN_PLAYER:
                            self.player = Player(x, y, self.game)
                        elif visual_space_types[t]['var'] is not None:
                            if not self.editor and t == loader.SOKOBAN_EMPTY:
                                continue
                            getattr(self, visual_space_types[t]['var']).add(visual_space_types[t]['obj'](x, y))

        self.size = Pair(data.shape[1], data.shape[0])

        self.objects.add(self.empties)
        self.objects.add(self.floors)
        self.objects.add(self.walls)
        self.objects.add(self.goals)
        self.objects.add(self.boxes)
        if self.player:
            self.objects.add(self.player)

        # Falak átalakítása a találkozásoknak megfelelő típusúra
        for wall in self.walls:
            wall.build(self)

        # Eltolás és Zsugorítás/Nagyítás arányának meghatározása
        self.recalc_size()

    def __getitem__(self, i):
        """adatok visszaadása a kétdimenziós tömbböl"""
        if hasattr(i, '__getitem__') and len(i) == 2:
            x = i[0]
            y = i[1]

            if x < 0 or y < 0:
                raise IndexError

            return self.raw[y,x]
        
        return None

    def __setitem__(self, i, value):
        """a pályaadatok szerkesztése kétdimenziós tömbként
        
        A pályaszerkesztő miatt."""
        if not hasattr(i, '__getitem__') or len(i) < 2:
            return
        
        x = i[0]
        y = i[1]

        self.raw[y,x] = value

        # Ha a Space-t a pályaszerkesztő használja a pálya adatainak megváltozása
        # következtében a látható objektumokat is meg kell változtatni.
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
        """A pálya méretének megváltozása esetén az eltolási és méretezési adatok
        újraszámolása"""
        canvas_size = self.size * TILE_RESOLUTION
        screen_size = self.space_size

        self.offset = screen_size * 0.5

        x_rate, y_rate = screen_size.p1 / canvas_size.p1, screen_size.p2 / canvas_size.p2
        rate = min(x_rate, y_rate)
        self.scale = rate

    def add_row(self):
        """Új sort hozzáadása a pályához""" #TODO: ellenőrizni
        if self.raw.shape[0] == 100:
            return
        cols = self.raw.shape[1]
        self.raw = np.r_[self.raw, np.ones((1,cols), np.byte)]
        self.size.p2 += 1
        self.recalc_size()

    def add_column(self):
        """Új oszlop hozzáadása a pályához""" #TODO: ellenőrizni
        rows = self.raw.shape[0]
        self.raw = np.c_[self.raw, np.ones(rows, np.byte)]
        self.size.p1 += 1
        self.recalc_size()

    def remove_row(self):
        """Sor törlése a pályából"""
        if self.raw.shape[0] == 3:
            return
        self.raw = self.raw[:-1]
        self.size.p2 -= 1
        self.recalc_size()

    def remove_column(self):
        """Oszlop törlése a pályából"""
        if self.raw.shape[1] == 3:
            return
        self.raw = self.raw[:,:-1]
        self.size.p1 -= 1
        self.recalc_size()

    def is_row_empty(self, row):
        """Lekérdezés, hogy egy sor csak Empty objektumokat tartalmaz-e
        
        Attr:
            row: int az ellenőrizni kívánt sor száma"""
        return np.all(np.equal(self.raw[row], loader.SOKOBAN_EMPTY))

    def is_column_empty(self, column):
        """Lekérdezés, hogy egy oszlop csak Empty objektumokat tartalmaz-e
        
        Attr:
            row: int az ellenőrizni kívánt oszlop száma"""
        return np.all(np.equal(self.raw[:,column], loader.SOKOBAN_EMPTY))

    """TODO: editornak külön ellenőrző osztályt kell írni
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
    """

    def draw(self, surface, pos = (0,0), down = False, grid = False):
        """Pályatér kirajzolása

        Args:
            surface(pygame.Surface): A felület amire ki kell rajzolni a játékteret
            pos(tuple[int,int]): a pálya pozíciója a felületen
            down(bool): a pálya lentre igazítva jelenik meg
            grid(bool): négyzetrács rajzolása a pályára
        """
        bg = pg.Surface(self.space_size)
        bg.fill(SPACE_BG_COLOR)
        canvas = pg.Surface(self.size * TILE_RESOLUTION, pg.SRCALPHA)

        # Objektumok kirajzolása
        for obj in self.objects:
            obj.draw(canvas)
        
        # Négyzetrács kirajzolása
        if grid:
            for y in range(self.raw.shape[0]):
                for x in range(self.raw.shape[1]):
                    pos = Pair(x,y) * TILE_RESOLUTION
                    pg.draw.rect(canvas, (150,150,150), pos + TILE_RESOLUTION, 1)

        # Játéktér méretezése
        if self.scale != 1:
            canvas = pg.transform.scale(canvas, self.size * self.scale * 32)

        # Igazítás
        rect = canvas.get_rect()
        if down:
            rect.centerx = self.offset.p1
            rect.bottom = self.space_size.p2
        else:
            rect.center = self.offset
        
        bg.blit(canvas, rect)
        surface.blit(bg, pos)
