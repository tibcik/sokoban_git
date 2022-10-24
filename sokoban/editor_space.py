""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: editor_space.py
Verzió: 1.0.0
--------------------
sokoban.editor_space

Játéktér a pályaszerkesztőhőz, az eredeti Space objektum másolata náhány kiegészítéssel.
"""
from __future__ import annotations
from math import floor

import pygame as pg
import numpy as np

from .objects import *
from utils import Pair, betweens
from .data import loader
from .config import TILE_RESOLUTION, SPACE_BG_COLOR

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .editor import Editor

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
        editor (Editor): a pályaszerkesztő
        set_name (str): a pályakészlet neve
        level (int): a pálya száma a pályakészletben
        space_size (Pair): a játéktér megjelnítésére lévő kép mérete
        size (Pair): a játéktér tényleges mérete
        scale (floot): a megjelenítésre szükséges hely és a tényleges hely arányszáma
        offset (Pair): x, y eltolás értéke(pl.: a pálya közepré igazítása érdekében)
        raw (NumpyArray): a pálya aktuális állását replezentáló két dimenziós tömb
        objects (pygame.sprite.Group): a játéktéren megjelenített objektumok gyűjteménye
        empties: pygame.sprite.Group a játéktéren kívüli csempék gyűjteménye
        floors: pygame.sprite.Group a játéktéren belüli csempék(padló) gyűjteménye
        walls: pygame.sprite.Group a fal csempék gyűjteménye
        goals: pygame.sprite.Group a dobozok végső helyeinek gyűjteménye
        boxes: pygame.sprite.Group a dobozok gyűjteménye
        player: sokoban.objects.Player a karakter objektuma
        static_image (pygame.Surface): a statikus objektumok képe
        background (pygame.Surface): háttérkép
        selected (Pair): a kiválasztott játékmező"""
    def __init__(self, space_size: Pair, editor: Editor, set_name: str,
        level: int):
        """belépési pont
        
        Args:
            space_size: a játéktér megjelnítésére lévő kép mérete
            editor: a pályaszerkesztő
            set_name: a pályakészlet neve
            level: a pálya száma a pályakészletben"""
        self.editor = editor
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

        self.static_image = None
        from pygame_menu.utils import image_loader
        self.background = image_loader("profile_back.png")

        self.selected = Pair(0,0)

        self.init_level()

    def init_level(self):
        """Meglévő pálya betöltése
        """
        assert loader.jget_info(None, self.set_name) is not None, (f"A \"{self.set_name}\" nem"
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
                            self.player = Player(x, y, None)
                        elif visual_space_types[t]['var'] is not None:
                            #if not self.editor and t == loader.SOKOBAN_EMPTY:
                            #    continue
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
    
    def __iter__(self):
        self.__element_index = 0
        self.__delimiter = False
        return self

    def __next__(self):
        if self.__delimiter:
            self.__delimiter = False
            return None

        x = self.__element_index % self.raw.shape[1]
        y = floor(self.__element_index / self.raw.shape[1])

        if y >= self.raw.shape[0]:
            raise StopIteration

        self.__element_index += 1
        if self.__element_index % self.raw.shape[1] == 0:
            self.__delimiter = True

        return self.raw[y,x]

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
        empty = Empty(x, y)
        pg.sprite.spritecollide(empty, self.objects, True)
        for t in visual_space_types:
            if t & value:
                if t == loader.SOKOBAN_PLAYER:
                    v_obj = visual_space_types[t]['obj'](x, y, None)
                    self.player = v_obj
                else:
                    v_obj = visual_space_types[t]['obj'](x, y)
                    getattr(self, visual_space_types[t]['var']).add(v_obj)
                self.objects.add(v_obj)

        for wall in self.walls:
            wall.build(self)

        self.static_image = None

    def recalc_size(self):
        """A pálya méretének megváltozása esetén az eltolási és méretezési adatok
        újraszámolása"""
        canvas_size = self.size * TILE_RESOLUTION
        screen_size = self.space_size

        self.offset = screen_size * 0.5

        x_rate, y_rate = screen_size.p1 / canvas_size.p1, screen_size.p2 / canvas_size.p2
        rate = min(x_rate, y_rate)
        self.scale = rate

        self.static_image = None

    def reshape(self, width: int, height: int):
        """reshape Pálya méretének megváltoztatása

        Args:
            width (int): szélesség
            height (int): magasság
        """
        width = betweens(width, 3, 100)
        height = betweens(height, 3, 100)
        tmp_arr = np.ones((height,width), np.byte)

        min_width = min(width, self.raw.shape[1])
        min_height = min(height, self.raw.shape[0])

        for x in range(min_height):
            for y in range(min_width):
                tmp_arr[x,y] = self.raw[x,y]

        self.init_level_data(tmp_arr)

    def draw(self, surface, pos = (0,0)):
        """Pályatér kirajzolása

        Args:
            surface(pygame.Surface): A felület amire ki kell rajzolni a játékteret
            pos(tuple[int,int]): a pálya pozíciója a felületen
        """
        bg = pg.Surface(self.space_size)
        bg.fill(SPACE_BG_COLOR)
        if self.background:
            bg.blit(self.background, (0,0))
        canvas = pg.Surface(self.size * TILE_RESOLUTION, pg.SRCALPHA)

        if self.static_image is None:
            self.static_image = pg.Surface(self.size * TILE_RESOLUTION, pg.SRCALPHA)
            for obj in self.walls:
                obj.draw(self.static_image)
            for obj in self.floors:
                obj.draw(self.static_image)
            for obj in self.goals:
                obj.draw(self.static_image)
            for obj in self.empties:
                obj.draw(self.static_image)
            
            if self.scale != 1:
                self.static_image = pg.transform.scale(self.static_image, self.size * self.scale * 32)

        # Objektumok kirajzolása
        for obj in self.boxes:
            obj.draw(canvas)
        if self.player is not None:
            self.player.draw(canvas)
        
        # Négyzetrács kirajzolása
        for y in range(self.raw.shape[0]):
            for x in range(self.raw.shape[1]):
                gpos = Pair(x,y) * TILE_RESOLUTION
                if self.selected == (x, y):
                    pg.draw.rect(canvas, (255,150,150), (gpos.p1,gpos.p2,TILE_RESOLUTION[0],TILE_RESOLUTION[1]), 2)
                else:
                    pg.draw.rect(canvas, (150,150,150), (gpos.p1,gpos.p2,TILE_RESOLUTION[0],TILE_RESOLUTION[1]), 1)

        # Játéktér méretezése
        if self.scale != 1:
            canvas = pg.transform.scale(canvas, self.size * self.scale * 32)

        # Igazítás
        rect = canvas.get_rect()
        rect.center = self.offset
        
        #bg.blit(canvas, rect)
        bg.blit(self.static_image, rect)
        bg.blit(canvas, rect)
        surface.blit(bg, pos)
