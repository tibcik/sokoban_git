""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: textentry.py
Verzió: 1.0.0
--------------------
pygame_menu.components.textentry

Szövegbeviteli menüelemek

Osztályok:
    TextEntry
    MultiTextEntry
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *
from utils import Pair

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    pass

class TextEntry(Scrollable, KeyboardGrabber, Selectable, Component):
    """Select osztály.

    Container osztályban felhasználható textentry menüelem. Az elembe lehet szöveget
    beírni, azon változtatni.
    
    Attributes:
        curzor (dict): a kurzor adatai {'last_blink': (int), 'blind': (bool), 'pos': (int)}
        pressed_key (dict | None): a lenyomott billenytűrűl tartalmat adatokat
        font(property) (pygame.font.Font): a gomb betűtipusa
        value(property) (str): az elemben lévő szöveg"""
    def __init__(self, container: Container, value: str = '', font_size: int = config.DEFAULT_FONT_SIZE, **kwargs):
        """belépési pont
        
        Args:
            container: a befogalaló container
            value: az elemben megjelenő szöveg. Defaults to ''.
            font_size (int): a szöveg mérete. Defaults to config.DEFAULT_FONT_SIZE.
        
        Kwargs:
            -> Component.__init__(...)"""
        Component.__init__(self, container, **kwargs)

        assert 'size' in kwargs, f"A TextEntry elemnek kötelező megadni a méretét!"

        self.value = value
        self.font = config.get_font(config.TEXTENTRY_FONT, font_size)

        self.cursor = {'last_blink': 0, 'blind': False, 'pos': 0}

        self.pressed_key = None

        self.color['bg'] = config.TEXTENTRY_DEFAULT_COLOR
        self.color['focus'] = config.TEXTENTRY_FOCUS_COLOR
        self.color['select'] = config.TEXTENTRY_SELECT_COLOR
        self.color['kgrabbed'] = config.TEXTENTRY_KGRABBED_COLOR
        self.color['font'] = config.TEXTENTRY_FONT_COLOR

        self._selected = False

    @property
    def value(self) -> str:
        """getter"""
        return self._value

    @value.setter
    def value(self, value: str):
        """setter
        
        Raises:
            ValueError: Ha nem str típusú"""
        ex.arg_type_exception('value', value, str)
        self._value = value

        self.updated()

    @property
    def font(self) -> pg.font.Font:
        """getter"""
        return self._font

    @font.setter
    def font(self, value: pg.font.Font):
        """setter
        
        Raises:
            ValueError: Ha nem pygame.font.Font osztály leszármazottja"""
        ex.arg_instance_exception('value', value, pg.font.Font)
        
        self._font = value

        self.updated()

    @property
    def select(self):
        """getter"""
        return self._selected

    @select.setter
    def select(self, value):
        """setter"""
        if not value:
            self.release_keyboard()
        self._selected = value

        self.updated()

    def get_text_size(self):
        """A megjelítendő szöveg mérete."""
        return Pair(6, 6) + Pair(self.font.size(self.value))

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        # Méret meghatározása és beállítása
        # Ha megváltozott a méret akkor hozzá kell igazítani a kép méretét, de
        # minimum annyinak kell lennie mint a beállított méret
        tsize = self.get_text_size()
        tsize = (max(self.size[0], tsize[0]), max(self.size[1], tsize[1]))
        if tsize != self.image.get_size():
            self.image = pg.Surface(tsize)

        if self.keyboard_grabbed:
            self.image.fill(self.color['kgrabbed'])
        elif self.select:
            self.image.fill(self.color['select'])
        elif self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])

        # Mivel a kirajzoláshoz úgy is meg kell határozni a kurzor előtt lévő
        # szöveg méretét, ezért itt állítjuk be a scroll értéket is ha kell
        cursor_xpos = self.font.size(self.value[0:self.cursor['pos']])[0]

        if self.scroll[0] > cursor_xpos:
            self.scroll = {'x': cursor_xpos}
        elif (self.size[0] + self.scroll[0]) < (cursor_xpos + 6):
            self.scroll = {'x': cursor_xpos - self.size[0] + 6}

        # Törlésnél lehet kisebb de a scroll értéke nem változik ezért szükséges
        # ebben az esetben frissíteni a scroll értéket
        if self.image.get_width() < (self.size[0] + self.scroll[0]):
            self.scroll = {'none': None}

        # A kurzor megjelenítése
        if not self.cursor['blind']:
            pg.draw.line(self.image, self.color['font'], (3 + cursor_xpos,3),
                (3 + cursor_xpos,self.size[1] - 3))

        # A szöveg kiírása
        rendered = self.font.render(self.value, True, self.color['font'])
        self.image.blit(rendered, (3,3))

    def e_MouseButtonUp(self, **kwargs):
        """egér gombelengedés kezelése
        
        Kwargs:
            pos (tuple): az mutató pozíciója
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        self.keyboard_grabbed = True
        self.updated()

    def e_KeyDown(self, unicode, key, **kwargs):
        """billentyűzet gombnyomásának lekezelése

        Args:
            unicode (char): a lenyomott billentyű unicode értéke
            key (int): a billentyű kódja
        
        Kwargs:
            mod (int): módosítóbillentyűk
            scancode (int?): a lenyomott billenytű scancode értéke
            
        Return:
            bool: gomblenyomás továbbra is feldolgozandó"""
        if self.keyboard_grabbed:
            # Nyilag lenyomásának hatására a curzor pozíciója változik
            if key == pg.K_LEFT:
                if self.cursor['pos'] > 0:
                    self.cursor['pos'] -= 1
            elif key == pg.K_RIGHT:
                if self.cursor['pos'] < len(self.value):
                    self.cursor['pos'] += 1
            elif key == pg.K_UP:
                    self.cursor['pos'] = 0
            elif key == pg.K_DOWN:
                    self.cursor['pos'] = len(self.value)
            # Karakter törlése
            elif key == pg.K_BACKSPACE:
                if self.cursor['pos'] > 0:
                    self.value = (self.value[0:self.cursor['pos']-1] + 
                        self.value[self.cursor['pos']:])
                    self.cursor['pos'] -= 1
            elif key == pg.K_DELETE:
                if self.cursor['pos'] < len(self.value):
                    self.value = (self.value[0:self.cursor['pos']] + 
                        self.value[self.cursor['pos']+1:])
            # Enter vagy esc billenytű hatására a componens elengefi az egeret
            elif key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_ESCAPE):
                    self.release_keyboard()
            # Karakter hizzáadása a szöveghez
            elif unicode != '':
                self.value = (self.value[0:self.cursor['pos']] + unicode +
                    self.value[self.cursor['pos']:])
                self.cursor['pos'] += 1

            # A karakter lenyomásának megjegyzése
            if self.keyboard_grabbed:
                kwargs['unicode'] = unicode
                kwargs['key'] = key
                self.pressed_key = {'last_tick': pg.time.get_ticks(), 'data': kwargs}

            self.updated()

            # A billenytyűlenyomások lekezelésének megakadályozása a containerben
            return True
        else:
            # Ha még nem volt elkapva a billenytűzet, de az elem ki van választva
            # akkor bármely szöveg gomb lenyomására az elem elkapja a billenytűzetet
            if unicode != '':
                self.keyboard_grabbed = True

                self.updated()
                return True
        
        return False

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        self.pressed_key = None

    def update(self):
        """frissítés
        
        Curzor villogtatása, lenyomott gomb ismételgetése."""
        # Ha nincs kiválasztva de a curzor látható akkor eltüntetjük a curzort
        if not self.select:
            if not self.cursor['blind']:
                self.cursor['blind'] = True
                self.updated()
            return
        # Ha ki van választva akkor megjelenítjük a curzort
        elif not self.keyboard_grabbed:
            if self.cursor['blind']:
                self.cursor['blind'] = False
                self.updated()
            return
        # Ha ki van választva és el van kapva a billenytűzet:
        # Villogtatjuk a kurzort
        now = pg.time.get_ticks()
        if (now - self.cursor['last_blink']) > 500:
            self.cursor['blind'] = not self.cursor['blind']

            self.updated()
            self.cursor['last_blink'] = now

        # Ha van lenyomva billenytű akkor annak adatai újra és újra elküldjük
        # lekezelésre amíg fel nem engedjük a billentyűt
        if self.pressed_key is not None and now - self.pressed_key['last_tick'] > 250:
            self.e_KeyDown(**self.pressed_key['data'])
            self.pressed_key['last_tick'] = now - 200

class MultiTextEntry(TextEntry):
    def get_text_size(self):
        """A megjelítendő szöveg mérete."""
        return Pair(6, 6) + Pair(self.font.size(self.value))
    def get_text_size(self):
        """A megjelítendő szöveg mérete."""

        size = Pair(6, 6)

        lines = self.value.split("\n")
        for line in lines:
            lsize = self.font.size(line)
            size.p1 = max(size.p1, lsize[0]) + 6
            size.p2 += self.font.get_height()

        return size

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        # Méret meghatározása és beállítása
        # Ha megváltozott a méret akkor hozzá kell igazítani a kép méretét, de
        # minimum annyinak kell lennie mint a beállított méret
        tsize = self.get_text_size()
        tsize = (max(self.size[0], tsize[0]), max(self.size[1], tsize[1]))
        if tsize != self.image.get_size():
            self.image = pg.Surface(tsize)

        if self.keyboard_grabbed:
            self.image.fill(self.color['kgrabbed'])
        elif self.select:
            self.image.fill(self.color['select'])
        elif self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])
        
        lh = self.font.get_height()
        lines = self.value.split("\n")
        chars_count = 0
        for i in range(len(lines)):
            line = lines[i]
            # Ha abban a sorban vagyunk ahol a cursor van
            if (self.cursor['pos'] >= chars_count and self.cursor['pos'] <= 
                (chars_count + len(line))):
                cursor_xpos = self.font.size(line[0:(self.cursor['pos']-chars_count)])[0]

                # Mivel a kirajzoláshoz úgy is meg kell határozni a kurzor előtt lévő
                # szöveg méretét, ezért itt állítjuk be a scroll értéket is ha kell
                if self.scroll[0] > cursor_xpos:
                    self.scroll = {'x': cursor_xpos}
                elif (self.size[0] + self.scroll[0]) < (cursor_xpos + 6):
                    self.scroll = {'x': cursor_xpos - self.size[0] + 6}
                if self.scroll[1] > i * lh:
                    self.scroll = {'y': i * lh}
                elif (self.size[1] + self.scroll[1]) < ((i + 1) * lh + 6):
                    self.scroll = {'y': (i + 1) * lh - self.size[1] + 6}

                # Törlésnél lehet kisebb de a scroll értéke nem változik ezért szükséges
                # ebben az esetben frissíteni a scroll értéket
                if self.image.get_width() < (self.size[0] + self.scroll[0]):
                    self.scroll = {'none': None}
                if self.image.get_height() < (self.size[1] + self.scroll[1]):
                    self.scroll = {'none': None}

                if not self.cursor['blind']:
                    pg.draw.line(self.image, self.color['font'], (3+cursor_xpos,lh*i+3),
                        (3 + cursor_xpos,lh*(i + 1)))
            rendered = self.font.render(line, True, self.color['font']) #TODO config
            self.image.blit(rendered, (3,lh*i+3))
            chars_count += len(line) + 1

    def e_KeyDown(self, unicode, key, **kwargs):
        """billentyűzet gombnyomásának lekezelése

        Args:
            unicode (char): a lenyomott billentyű unicode értéke
            key (int): a billentyű kódja
        
        Kwargs:
            mod (int): módosítóbillentyűk
            scancode (int?): a lenyomott billenytű scancode értéke
            
        Return:
            bool: gomblenyomás továbbra is feldolgozandó"""
        if self.keyboard_grabbed:
            # Nyilak lenyomásának hatására a curzor pozíciója változik
            if key == pg.K_LEFT:
                if self.cursor['pos'] > 0:
                    self.cursor['pos'] -= 1
            elif key == pg.K_RIGHT:
                if self.cursor['pos'] < len(self.value):
                    self.cursor['pos'] += 1
            elif key == pg.K_UP:
                t_break = self.value.rfind('\n', 0, self.cursor['pos'])
                pre_break = self.value.rfind('\n', 0, t_break)
                self.cursor['pos'] = (pre_break + 1) if t_break != -1 else 0
            elif key == pg.K_DOWN:
                t_break = self.value.find('\n', self.cursor['pos'])
                self.cursor['pos'] = (t_break + 1) if t_break != -1 else len(self.value)
            # Karakter törlése
            elif key == pg.K_BACKSPACE:
                if self.cursor['pos'] > 0:
                    self.value = (self.value[0:self.cursor['pos']-1] + 
                        self.value[self.cursor['pos']:])
                    self.cursor['pos'] -= 1
            elif key == pg.K_DELETE:
                if self.cursor['pos'] < len(self.value):
                    self.value = (self.value[0:self.cursor['pos']] + 
                        self.value[self.cursor['pos']+1:])
            # Multiline módban az enter billentyű hatására sortörést rakunk be
            elif key in (pg.K_RETURN, pg.K_KP_ENTER):
                self.value = (self.value[0:self.cursor['pos']] + "\n" + 
                    self.value[self.cursor['pos']:])
                self.cursor['pos'] += 1
            elif key == pg.K_ESCAPE:
                self.release_keyboard()
            # Karakter hizzáadása a szöveghez
            elif unicode != '':
                self.value = (self.value[0:self.cursor['pos']] + unicode +
                    self.value[self.cursor['pos']:])
                self.cursor['pos'] += 1

            # A karakter lenyomásának megjegyzése
            if self.keyboard_grabbed:
                kwargs['unicode'] = unicode
                kwargs['key'] = key
                self.pressed_key = {'last_tick': pg.time.get_ticks(), 'data': kwargs}

            self.updated()

            # A billenytyűlenyomások lekezelésének megakadályozása a containerben
            return True
        else:
            # Ha még nem volt elkapva a billenytűzet, de az elem ki van választva
            # akkor bármely szöveg gomb lenyomására az elem elkapja a billenytűzetet
            if unicode != '':
                self.keyboard_grabbed = True

                self.updated()
                return True
        
        return False