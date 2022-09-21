"""Játékhoz kapcsolódó kiegészítő elemek

A Sokoban játékhoz kapcsolódó kiegészítő eszközök amiknek egy része tesztelési
célt szolgál.
"""
from __future__ import annotations

import pygame as pg

from sokoban import config
from sokoban.config import DEFAULT_FONT, SMALL_FONT_SIZE #TODO: refactiring

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class FpsDisplay:
    """Fps kijelzésére szolgáló osztály
    
    Tesztelés alatt használható."""
    def __init__(self, clock):
        self.font = config.get_font(config.DEFAULT_FONT, 14)
        self.clock = clock

    def draw(self, surface):
        image = pg.Surface((50,30), pg.SRCALPHA)
        image.fill((255,255,255,125))
        fps = str(int(self.clock.get_fps()))
        fps_text = self.font.render(fps, 1, (0,0,0))
        image.blit(fps_text, (10,10))
        surface.blit(image, (0,0))

__all__ = ["FpsDisplay"]

class Statistic(pg.sprite.Sprite):
    """A játék statisztikáit megjelenítő osztály
    
    Attributes:
        image (pygame.Surface): A statisztika képe
        rect (pygame.rect.Rect): A kirajzolandó kép határai
        font (pygame.font.Font): A betűkéslet amivel a szöveget kiírjuk"""
    def __init__(self):
        """Statistic"""
        super().__init__()

        self.image = pg.Surface((500, 32), pg.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.topright = (0, 0)

        self.font = config.get_font(DEFAULT_FONT, SMALL_FONT_SIZE)
        
        self.update(0,0,"Megoldás - ?")

    def format_time(self, elapsed_time: float) -> str:
        """Másodpercek átalakítása szöveggé

        Args:
            elapsed_time (float): eltelt idő

        Returns:
            str: 00:00 formátumú idő
        """
        secs = int(elapsed_time)
        if secs > 5999:
            secs = 5999
        return "Eltelt idő: {:02d}:{:02d}".format(int(secs / 60), secs % 60)

    def format_moves(self, moves: int) -> str:
        """Lépések átalakítása szöveggé

        Args:
            moves (int): lépések száma

        Returns:
            str: 0000 formátumú szöveg
        """
        if moves > 9999:
            moves = 9999

        return "Lépések: {:4d}".format(moves)

    def update(self, elapsed_time: float, moves: int, solution):
        """adatok frissítása

        Args:
            elapsed_time (float): eltelt idő
            moves (int): lépések száma
        """
        elapsed_time_text = self.font.render(self.format_time(elapsed_time), True, 
            config.STATISTIC_FONT_COLOR)
        moves_text = self.font.render(self.format_moves(moves), True,
            config.STATISTIC_FONT_COLOR)
        solution_text = self.font.render(solution, True,
            config.STATISTIC_FONT_COLOR)
        self.image.fill(config.STATISTIC_BG_COLOR)
        self.image.blit(elapsed_time_text, (10, 5))
        self.image.blit(moves_text, (180, 5))
        self.image.blit(solution_text, (350, 5))