"""Játékhoz kapcsolódó kiegészítő elemek

A Sokoban játékhoz kapcsolódó kiegészítő eszközök amiknek egy része tesztelési
célt szolgál.
"""
from __future__ import annotations

import pygame as pg

import config #TODO: refactiring

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