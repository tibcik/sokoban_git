""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: component.py
Verzió: 1.0.0
--------------------
pygame_menu.components.component

Menu component ősosztályok.

Mineden menu és container componens a Component osztály leszármazottja. Ezek
mellett a viselkedésük megváltoztatására van néhány egyébb osztály amelynek
leszármazottja lehet egy container componens.
Osztályok:
    Component: Minden menu és container componens ősosztálya
    Scrollabel: Azon komponensek amiknek a mérete nagyobb lehet mint a számukra
        biztosított méret
    Selectable: A kiválasztható komponensek
    MouseGrabber: Amik az egérlenyomás után annak felengedéséig nem engedik el
        az egér eszközt
    KeyboardGrabber: Amik megakadályozzák, hogy egy billentyű lenyomása a container
        objektumhoz kerüljön

Konstansok:
    STICKY_... a komponens pozícionálása adott oldalhoz

Használat:
    class Foo(Component):
    
    class Bar(MouseGrabber, Selectable, Component):

Osztályok:
    Component
    Scrollable
    Selectable
    MouseGrabber
    KeyboardGrabber
Konstansok:
    STICKY_UPLEFT
    STICKY_UP
    STICKY_UPRIGHT
    STICKY_RIGHT
    STICKY_DOWNRIGTH
    STICKY_DOWN
    STICKY_DOWNLEFT
    STICKY_LEFT
    STICKY_CENTER
"""
from __future__ import annotations

import pygame as pg

from ..utils import EventHandler
from utils import Pair, betweens

import utils.exceptions as ex

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .container import Container

STICKY_UPLEFT = (0,0)
STICKY_UP = (0.5,0)
STICKY_UPRIGHT = (1,0)
STICKY_RIGHT = (1,0.5)
STICKY_DOWNRIGHT = (1,1)
STICKY_DOWN = (0.5,1)
STICKY_DOWNLEFT = (0,1)
STICKY_LEFT = (0,0.5)
STICKY_CENTER = (0.5,0.5)

class Component(EventHandler, pg.sprite.Sprite):
    """Ősosztálya minden menu és container componensnek.

    Az osztály megvalósítja egy componens alapvető feladatait. A componens
    kinézetére hatással lévő adattagok property típusúak a lekezelheztőség
    érdekében. Abstract módon metódust biztosít a kinézet megváltoztatására.
    Kirajzolja a kész képet a kapott pg.Surface objektumra.

    Attributes:
        container (Container | None): None értéket csak akkor vehet fel, ha maga is Container
        image (pygame.Surface): A componens vizuális megjelenése
        position(property) (Pair): a componens bal felső pontja a container-hez képest
        size(property) (Pair): a componens megjelenített mérete
        sticky(property) (tuple(int, int)): a komponens pozícionálása adott oldalhoz
        focus(property) (bool): a componens fokuszban van-e
        show (bool): a componens látható-e
        color(propery) (dict): (r,g,b,a) formában tárol színeket, lehetséges elemek: bg, focus, font
        _updated (bool): a componens frissűlt a legutólsó draw óta, következő rajzolásnál szükséges az image frissítése
        rect(property, csak getter) (pygame.rect.Rect): a pozíciót és a méretet tartalmazza
        area(property, csak getter) (pygame.rect.Rect): csak a méretet tartalmazza
        id (any): szabadon használható azonosító"""
    def __init__(self,
            container: Container | None,
            position: tuple(int, int) = (0,0),
            size: tuple(int, int) = (0,0),
            sticky: tuple(int, int) = STICKY_UPLEFT,
            id: any = None
        ):
        """Component

        Args:
            container (Container | None): az componenst befoglaló osztály
            position (tuple[int,int]): a componens pozíciója az őt befoglaló container-en belül. Defaults to (0,0).
            size (tuple[int,int]): a componens látható mérete. Defaults to (0,0).
            sticky (tuple[int,int]): a componens pozícionálása a position-hoz képest. Defaults to STICKY_UPLEFT.
            id (any): szabadon használható azonosító. Defaults to None.
        """
        pg.sprite.Sprite.__init__(self)

        self.id = id

        self.image = pg.Surface((0,0))

        # a container ellenőrzésére nincs lehetőség...
        self.container = container

        self.position = position
        self.size = size
        self.sticky = sticky

        self.focus = False
        self.show = True

        self._updated = False

        if self.container is not None:
            self.container.add(self)

        # Alap színek beállítása
        self._colors = {}
        self.color['bg'] = (0,0,0,255)
        self.color['focus'] = (255,0,0,255)

        self.updated()

    @property
    def position(self) -> Pair:
        """getter
        
        A pozíció a sticky értékétől fűgg."""
        pos = self._position
        
        return pos - (self.size * Pair(self.sticky))

    @position.setter
    def position(self, value: tuple[int, int]):
        """setter
        
        Args:
            value (tuple[int,int]): bármilyen legalább kételemű listaszerű objektum
            
        Raises:
            ValueError: Ha nem listaszerű
            IndexError: Ha kevesebb mint kételemű"""
        ex.arg_index_exception('value', value, 2)

        value = Pair(value)
        ivalue = Pair(value)
        ivalue.p1 = ivalue[0]
        ivalue.p2 = ivalue[1]

        if value != ivalue and self.container is not None:
            value = self.container.size * (abs(value - ivalue)) + ivalue

        self._position = value

        self.updated()

    @property
    def size(self) -> Pair:
        """getter"""
        return self._size

    @size.setter
    def size(self, value: tuple[int, int]):
        """setter
        
        Args:
            value (tuple[int, int]): bármilyen legalább kételemű listaszerű objektum
            
        Raises:
            ValueError: Ha nem listaszerű
            IndexError: Ha kevesebb mint kételemű"""
        ex.arg_index_exception('value', value, 2)

        self._size = Pair(value)

        self.updated()

    @property
    def sticky(self) -> tuple(int, int):
        """getter"""
        return self._sticky

    @sticky.setter
    def sticky(self, value: tuple[int, int]):
        """setter
        
        Args:
            value (tuple[int,int]): a STICKY konstansok egyike, vagy bármely kételemű listaszerű objektum
            
        Raises:
            ValueError: Ha a várt konstansok egyike"""
        ex.arg_constant_exeption('value', value, [globals()[x] for x in globals() if len(x) > 7 and x[0:7] == "STICKY_"])

        self._sticky = value

        self.updated()

    @property
    def focus(self) -> bool:
        """getter"""
        return self._focus

    @focus.setter
    def focus(self, value: bool):
        """setter"""
        self._focus = value

        self.updated()

    @property
    def color(self) -> dict:
        """getter"""
        return self._colors

    @color.setter
    def color(self, value: tuple[int, int, int, int]):
        """setter
        
        Minden szín beállítása azonos értékre"""
        for c_name in self.color:
            self._colors[c_name] = value

    @property
    def rect(self) -> pg.rect.Rect:
        """getter
        
        A componens pozíciója és mérete pygame.rect.Rect objektumként"""

        return pg.rect.Rect(self.position, self.size)

    @property
    def area(self) -> pg.rect.Rect:
        """getter
        
        A conponens mérete pygame.rect.Rect objektumként (0,0) pozícióval"""

        return pg.rect.Rect((0, 0), self.size)

    def updated(self):
        """elem megváltozásának jelzése"""
        self._updated = True
        if self.container is not None:
            self.container.updated()

    def update(self):
        pass

    def update_image(self):
        pass

    def draw(self, surface: pg.Surface):
        """component kirajzolása
        
        Args:
            surface (pygame.Surface): amire az elemet rajzolni kell"""
        if self.show:
            if self._updated:
                self.update_image()
                self._updated = False
            surface.blit(self.image, self.rect, self.area)

class Scrollable:
    """Scrollable conponent

    Csak a Component osztállyal együtt használható a következő formában:
    class Foo(.., Scrollable, ..., Component, ...)

    Attributes:
        scroll(property) (Pair): ennyivel mozdítja el a componenst a draw objektum mikor kirajzolja azt
        area(property, csak getter) (pygame.rect.Rect): a scroll pozíciója és a mérete"""
    @property
    def scroll(self) -> Pair:
        """getter"""
        if hasattr(self, '_scroll'):
            return self._scroll

        return Pair(0, 0)

    @scroll.setter
    def scroll(self, value):
        """setter
        
        Attr:
            value (dict | tuple): megadja vagy a relatív vagy az abszolút scroll pozíciót
                dict: {"x": abszolút, "y": absoulút, "relx": relatív, "rely": relatív}
                
        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk
            ValueError: Ha nem dict és nem listaszerű
            IndexError: Ha listaszerű, de kevesebb mint kételemű"""
        ex.instance_exception(self, Component)

        # Ha dict akkor a pozíciók meghatározása
        if type(value) == dict:
            x = value['x'] if 'x' in value else self.scroll[0]
            y = value['y'] if 'y' in value else self.scroll[1]
            x += value['relx'] if 'relx' in value else 0
            y += value['rely'] if 'rely' in value else 0
            value = (x, y)

        ex.arg_index_exception('value', value, 2)

        x = betweens(value[0], 0, self.image.get_width() - self.size[0])
        y = betweens(value[1], 0, self.image.get_height() - self.size[1])
        self._scroll = Pair(x, y)

        #self.updated()

    @property
    def area(self) -> pg.rect.Rect:
        """getter
        
        A conponens mérete pygame.rect.Rect objektumként scroll pozícióval
        
        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)
        
        return pg.rect.Rect(self.scroll, self.size)

class Selectable:
    """Kiválasztható conponent

    Csak a Component osztállyal együtt használható a következő formában:
    class Foo(.., Selectable, ..., Component, ...)

    Attributes:
        color(property) (dict): Az alap színeket kiegészíti a select értékkel
        select(property) (bool): a kiválasztás értéke
    """
    @property
    def color(self) -> dict:
        """getter

        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)
        
        if 'select' not in self._colors:
            self._colors['select'] = (0,255,0,255)

        return self._colors

    @color.setter
    def color(self, value: tuple[int, int, int, int]):
        """setter
        
        Minden szín beállítása azonos értékre"""
        for c_name in self.color:
            self._colors[c_name] = value

        self.updated()

    @property
    def select(self) -> bool:
        """getter"""
        if not hasattr(self, "_selected"):
            self._selected = False

        return self._selected

    @select.setter
    def select(self, value: bool):
        """setter
        
        A kiválasztást visszajelezzük az container osztálynak
        
        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)
        
        self._selected = value

        self.updated()

    @property
    def selectable(self):
        """getter"""
        if not hasattr(self, "_selectable"):
            self._selectable = True

        return self._selectable

    @selectable.setter
    def selectable(self, value):
        """setter"""

        if not value:
            self.select = False
        self._selectable = value

    @property
    def focus(self) -> bool:
        """getter"""
        return self._focus

    @focus.setter
    def focus(self, value: bool):
        """setter

        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)

        if self.selectable:
            self._focus = value
        else:
            self._focus = False

        self.updated()

class MouseGrabber:
    """Egér megfogó component

    Csak a Component osztállyal együtt használható a következő formában:
    class Foo(.., MouseGrabber, ..., Component, ...)

    Attributes:
        mouse_grabbed(property) (bool): az egér el van-e kapva
    """
    @property
    def mouse_grabbed(self) -> bool:
        """getter"""
        if not hasattr(self, "_mouse_grabbed"):
            self._mouse_grabbed = False

        return self._mouse_grabbed

    @mouse_grabbed.setter
    def mouse_grabbed(self, value: bool):
        """setter

        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)

        self._mouse_grabbed = value

        self.updated()

    def grab_mouse(self):
        """egér megfogása"""
        self.mouse_grabbed = True

    def release_mouse(self):
        """egér elengedése"""
        self.mouse_grabbed = False

class KeyboardGrabber:
    """Billentyűzet megfogó component

    Csak a Component osztállyal együtt használható a következő formában:
    class Foo(.., KeyboardGrabber, ..., Component, ...)

    Attributes:
        keyboard_grabbed(property) (bool): a billentyűzet el van-e kapva
    """
    @property
    def keyboard_grabbed(self) -> bool:
        """getter"""
        if not hasattr(self, "_keyboard_grabbed"):
            self._keyboard_grabbed = False

        return self._keyboard_grabbed

    @keyboard_grabbed.setter
    def keyboard_grabbed(self, value: bool):
        """setter

        Raises:
            TypeError: Ha nem a Component osztállyal együtt használjuk"""
        ex.instance_exception(self, Component)
        
        self._keyboard_grabbed = value

        self.updated()

    def grab_keyboard(self):
        """billentyűzet megfogása"""
        self.keyboard_grabbed = True

    def release_keyboard(self):
        """billentyűzet elengedése"""
        self.keyboard_grabbed = False