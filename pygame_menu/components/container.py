"""Container osztály.

Container osztályok szerepelhetnek a Menu osztályokban. A container osztály
hosonló feladatok lát el mint egy Menu osztály kibővítve, néhány extra funkcióval.
Elemei más Component típusú objektumok.
"""
from __future__ import annotations

import pygame as pg

from sokoban import config

from .component import *
from .button import Button #TODO: tesztelési céllal, kivenni
from .scrollbar import Scrollbar
from ..utils import VERTICAL, HORIZONTAL

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..menu import Menu

class Container(Selectable, Scrollable, Component):
    """Container osztály.

    Container osztályok szerepelhetnek a Menu osztályokban. A container osztály
    hosonló feladatok lát el mint egy Menu osztály kibővítve, néhány extra funkcióval.
    Elemei más Component típusú objektumok.
    
    Attributes:
        menu (Menu): objektum amiben a container van
        items (pygame.sprite.Group[Component]): componenseket tartalmazó Group
        selectable (list[Component]): a kiválasztható componensek
        default (bool): a Container a menu default objektuma
        selected(property) (Component): a kiválasztott component
        focused (Component): a fókuszált component
        xscroller (Scrollbar): Horizontális scollbar
        yscroller (Scrollbar): Vertikális scollbar
        focus(property) (bool): a componens fokuszban van-e
        select(setter) (bool): a componens ki van-e választva"""
    def __init__(self, menu: Menu, **kwargs):
        """belépési pont
        
        Args:
            menu (Menu): a contaninert befoglaló Menu objektum
        
        Kwargs:
            -> Component.__init__(...)"""
        Component.__init__(self, None, **kwargs)

        assert 'size' in kwargs, ("A Container osztálynak kötelező megadni a size "
            "argumentumot példányosításkot.")

        self.menu = menu
        self.menu.add(self)

        self.items = pg.sprite.Group()
        self.selectables = []

        self.default = False
        if 'default' in kwargs:
            self.default = True
            self.menu.set_default(self)

        self._selected = None
        self._focused = None
        self.selected: Component = None
        self.focused: Component = None

        self.xscroller = Scrollbar(self, orientation = HORIZONTAL)
        self.yscroller = Scrollbar(self, orientation = VERTICAL)

        # Színek beállítása a config/skin alapján
        self.color['bg'] = config.CONTAINER_DEFAULT_COLOR
        self.color['focus'] = config.CONTAINER_FOCUS_COLOR
        self.color['select'] = config.CONTAINER_SELECT_COLOR

    @property
    def focus(self):
        """getter"""
        return self._focus

    @focus.setter
    def focus(self, value: bool):
        """setter"""
        self._focus = value

        # Ha ki van választva akkor azért vesztette el a fókuszt
        # TODO: ezt felül kell vizsgálni
        """if not value and not self.select:
            for item in self.items:
                item.focus = False"""
        
        self.updated()

    @property
    def select(self) -> bool:
        """getter"""
        if not hasattr(self, "_select"):
            self._select = False

        return self._select

    @select.setter
    def select(self, value: bool):
        """setter"""
        self._select = value

        if not value:
            if isinstance(self.selected, KeyboardGrabber):
                self.selected.release_keyboard()
            # TODO: ezt felül kell vizsgálni
            """if isinstance(self.selected, Selectable):
                self.selected.select = False
                self.selected = None"""
        else:
            self.focus = False

        self.updated()

    @property
    def selected(self):
        """getter"""

        return self._selected

    @selected.setter
    def selected(self, value: Component | None):
        """setter"""
        assert isinstance(value, Component) or value is None, (f"Várt "
            f"pygame_menu.components.Component vagy None típus, kapott {type(value)}")
        if self._selected is not None:
            self._selected.select = False
        self._selected = value
        if self._selected is not None:
            self._selected.select = True

    @property
    def focused(self):
        """getter"""
        return self._focused

    @focused.setter
    def focused(self, value: Component | None):
        """setter"""
        if self._focused is not None:
            self._focused.focus = False
        self._focused = value
        if self._focused is not None:
            self._focused.focus = True

    def add(self, item):
        """component hozzáadása
        
        Belső használatra."""
        assert isinstance(item, Component), (f"Várt pygame_menu.components.Container "
            f"típus, kapott {type(item)}")
        
        self.items.add(item)
        if isinstance(item, Selectable):
            self.selectables.append(item)

        self.updated()

    def remove(self, item):
        """component eltávolítása
        
        Belső használatra."""
        assert isinstance(item, Component), (f"Várt pygame_menu.components.Container "
            f"típus, kapott {type(item)}")
        
        if self.items.has(item):
            self.items.remove(item)
            if item in self.selectables:
                self.selectables.remove(item)

        self.updated()

    def update(self):
        """frissítés"""
        self.items.update()
        #self.update_image()

    def get_image_size(self) -> Pair:
        """saját teljes méret meghatározása"""
        image_size = pg.rect.Rect(0,0,0,0)

        # Az összes componens méretének uniója
        for item in self.items:
            if isinstance(item, Scrollbar):
                continue
            image_size.union_ip(item.rect)
        
        # Ha a kép mérete kisebb lenne mint a component mérete akkor a méretet
        # használjuk
        if self.size.p1 >= image_size.width:
            image_size.width = self.size[0]
            if self.xscroller.show:
                self.xscroller.show = False
        else:
            image_size.width += 7
            if image_size.width != self.image.get_width():
                self.xscroller.show = True
        if self.size.p2 >= image_size.height:
            image_size.height = self.size[1]
            if self.yscroller.show:
                self.yscroller.show = False
        else:
            image_size.height += 7
            if image_size.height != self.image.get_height():
                self.yscroller.show = True

        return Pair(image_size.size)

    def update_image(self):
        """Kirajzolandó kép frissítése."""
        self.image = pg.Surface(self.get_image_size(), pg.SRCALPHA)

        if self.select:
            self.image.fill(self.color['select'])
        elif self.focus:
            self.image.fill(self.color['focus'])
        else:
            self.image.fill(self.color['bg'])

        [item.draw(self.image) for item in self.items]

        # A kiválasztott componens felülre hozása
        if self.selected is not None:
            self.selected.draw(self.image)

        # A scrollbar-ok felülre hozása
        self.xscroller.draw(self.image)
        self.yscroller.draw(self.image)

    def get_rel_mouse_pos(self, item: Component, pos: tuple(int, int)) -> Pair:
        """relatív egér pozíció meghatározása
        
        Args:
            item (Component): a vizsgálandó komponens
            pos (tuple[int,int]): az egérmutató pozíciója

        Returns:
            Pair: objektum a relatív egér pozícióval
        """

        return Pair(pos) - (item.position - self.scroll)

    def is_mouse_in_item(self, item: Component, pos: tuple(int, int)) -> bool:
        """Megvizsgálja, hogy az egér az item határain belül van-e
        
        Args:
            item (Component): a vizsgálandó komponens
            pos (tuple[int,int]): az egérmutató pozíciója
            
        Returns:
            bool: érték"""
        rpos = self.get_rel_mouse_pos(item, pos)
        test = (rpos.p1 > 0 and rpos.p2 > 0 and rpos.p1 < item.area.width and
            rpos.p2 < item.area.height)

        return test

    def get_focused(self, pos: tuple[int, int]) -> Component | None:
        """Az a komponens amin az egérmutató áll
        
        Args:
            pos (tuple[int,int]): az egérmutató pozíciója
            
        Returns:
            Component | None: Az egérmutatón álló komponens vagy None"""
        focused = None

        for item in self.items:
            if self.is_mouse_in_item(item, pos):
                if isinstance(item, Scrollbar) and not item.show:
                    continue
                focused = item
                break

        return focused

    def e_MouseButtonDown(self, **kwargs):
        """egér gomblenyomás kezelése
        
        Kwargs:
            pos (tuple): az mutató pozíciója
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        if kwargs['in']:
            if self.focused is not None:
                if isinstance(self.focused, MouseGrabber):
                    self.focused.grab_mouse()

                kwargs['pos'] = self.get_rel_mouse_pos(self.focused, kwargs['pos'])
                self.focused.e_MouseButtonDown(**kwargs)

    def e_MouseButtonUp(self, **kwargs):
        """egér gombelengedés kezelése
        
        Kwargs:
            pos (tuple): az mutató pozíciója
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        # Ha nem a container-en belül lett elengedve a gomb, az azt megfogó
        # component akkor is el kell engedje azt.
        if isinstance(self.focused, MouseGrabber):
            self.focused.release_mouse()
            #self.focused = None #TODO: nem emlékszem ezt miért írtam bele... van valami haszna?
        # ha van fókuszált component
        if self.focused is not None:
            focused = self.get_focused(kwargs["pos"])
            # ha ott engedtük el az egérgombot ahol lenyomtuk
            if focused == self.focused:
                if not isinstance(focused, Scrollbar):
                    if self.focused != self.selected:
                        self.selected = self.focused
                
                kwargs['pos'] = self.get_rel_mouse_pos(self.focused, kwargs['pos'])
                self.focused.e_MouseButtonUp(**kwargs)
            # ha nem ott akkor a fókuszt annak adjuk át ahol elengedtük az egeret
            # és elvesszük a fókuszt a fókuszált elemtől
            else:
                self.focused = focused

            if isinstance(self.focused, MouseGrabber):
                    self.focused.release_mouse()

    def e_MouseMotion(self, **kwargs):
        """egér mozgás kezelése
        
        Kwargs:
            pos (tuple): az mutató pozíciója
            rel (tuple): az egér relatív elmozdulása
            button (int): nyomvatartott gomb
            touch (bool): ?"""
        pos = kwargs['pos']

        # Ha a fókuszált componens megfogra az egeret, csak annak küldjük tovább
        # az eseményt.
        if isinstance(self.focused, MouseGrabber) and self.focused.mouse_grabbed:
            kwargs['pos'] = self.get_rel_mouse_pos(self.focused, pos)
            
            self.focused.e_MouseMotion(**kwargs)
            return

        # Ha a fókuszált elem megváltozott, azt beállítjuk a componensekben
        focused = self.get_focused(pos)
        if focused != self.focused:
            self.focused = focused

        if self.focused is not None:
            kwargs['pos'] = self.get_rel_mouse_pos(self.focused, pos)
            self.focused.e_MouseMotion(**kwargs)

    def e_MouseWheel(self, **kwargs):
        """egér görgőjének továbbadása

        Ha a vertikális scrollbar látszik akkor annak adjuk tovább az eseménye,
        ha nem akkor a horizontálisnak, ha az látszik. Ha az sem látszik akkor
        nem adjuk tovább az eseményt.
        
        Kwargs:
            witch (?): ?
            flipped (?): ?
            x (int): görgő x elmozdulása
            y (int): görgő y elmozdulása
            touch (bool): ?"""
        if isinstance(self.focused, Scrollbar):
            self.focused.e_MouseWheel(**kwargs)
        elif self.yscroller.show:
            self.yscroller.e_MouseWheel(**kwargs)
        elif self.xscroller.show:
            self.xscroller.e_MouseWheel(**kwargs)

    def get_next_item(self, way: str) -> Component:
        """Adott irányban lévő legközelebbi componenst adja vissza
        
        Args:
            way (str): left | up | right | down
            
        Return:
            Component | None, ha van elem abban az irányban akkor a legközelebbit
            adja vissza, ha nincs akkor None"""
        assert way in ['left', 'up', 'right', 'down'], (f"Várt left | up | right "
            f"| dowm, kapott {way}")
        
        if len(self.selectables) == 0:
            return None

        if self.selected is None:
            return self.selectables[0]

        selected = self.selected

        next_item = None
        next_dist = -1
        for item in self.selectables:
            if item == selected:
                continue

            dist = item.position - selected.position
            if way == 'left':
                dist = dist.p1 * -1
            elif way == 'up':
                dist = dist.p2 * -1
            elif way == 'right':
                dist = dist.p1
            elif way == 'down':
                dist = dist.p2
            if dist > 0 and (next_dist == -1 or dist < next_dist) and item.selectable:
                next_item = item
                next_dist = dist

        return next_item

    def e_KeyDown(self, **kwargs):
        """billentyűzet gombnyomásának lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a lenyomott billentyű unicode értéke
            scancode (int?): a lenyomott billenytű scancode értéke"""
        key = kwargs['key']

        # Ha az egeret egy elem elkapta akkor nem kezeljük le az eseményt.
        if isinstance(self.focused, MouseGrabber) and self.focused.mouse_grabbed:
            return

        # Ha a componens elkapta a billentyűzetet továbbadjuk neki a lekezelése
        if isinstance(self.selected, KeyboardGrabber) and self.selected.keyboard_grabbed:
            self.selected.e_KeyDown(**kwargs)
            return

        prevent = False
        if self.selected is not None:
            prevent = self.selected.e_KeyDown(**kwargs)
        # A lekezelő componens megakadályozhatja a további lekezelést.
        # Pl. a lekezelő objektum épp elkapta a billenytűzetet, ezért nem
        # akarja, hogy az event a továbbiakban lekezelődjön.
        if not prevent:
            if key == pg.K_ESCAPE and not self.default:
                self.menu.lose_selection(self)
                return
            if len(self.selectables) > 0:
                way = None
                next = None

                if key == pg.K_LEFT:
                    way = 'left'
                elif key == pg.K_UP:
                    way = 'up'
                elif key == pg.K_RIGHT:
                    way = 'right'
                elif key == pg.K_DOWN:
                    way = 'down'

                if way is not None:
                    next = self.get_next_item(way)

                if next is not None:
                    self.selected = next

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        # Ha az egeret egy elem elkapta akkor nem kezeljük le az eseményt.
        if isinstance(self.focused, MouseGrabber) and self.focused.mouse_grabbed:
            return

        if self.selected is not None:
            self.selected.e_KeyUp(**kwargs)