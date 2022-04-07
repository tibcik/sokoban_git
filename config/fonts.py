import pygame as pg

SMALLEST_FONT_SIZE = 12
SMALL_FONT_SIZE = 18
DEFAULT_FONT_SIZE = 24
BIG_FONT_SIZE = 30
BIGGEST_FONT_SIZE = 36

DEFAULT_FONT = './data/karma.suture-regular.otf'
BUTTON_FONT = './data/karma.suture-regular.otf'
LABEL_FONT = './data/karma.suture-regular.otf'
TEXTENTRY_FONT = './data/karma.suture-regular.otf'
SELECT_FONT = './data/karma.suture-regular.otf'

fonts = {}

def get_font(font_name = DEFAULT_FONT, font_size = DEFAULT_FONT_SIZE):
    global fonts

    return pg.font.Font(font_name, font_size)

def set_font(font_name, font):
    global fonts

    if font_name not in fonts or isinstance(font, pg.font.Font):
        return

    fonts[font_name] = font

__all__ = [
    'SMALLEST_FONT_SIZE',
    'SMALL_FONT_SIZE',
    'DEFAULT_FONT_SIZE',
    'BIG_FONT_SIZE',
    'BIGGEST_FONT_SIZE',
    'DEFAULT_FONT',
    'BUTTON_FONT',
    'LABEL_FONT',
    'TEXTENTRY_FONT',
    'SELECT_FONT',
    'get_font', 'set_font']