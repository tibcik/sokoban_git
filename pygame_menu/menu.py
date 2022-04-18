"""Menu osztály tárolására szolgáló belső modul

Az osztály a pygame.sprite.Sprite osutály leszármazottja, ezért a
pygame.sprite.Group objektumhoz hozzáadható.
"""
from __future__ import annotations

import pygame as pg

from utils import Pair

from .utils import EventHandler
from .components import Container
from .components.component import MouseGrabber

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .components.component import Component

class Menu(EventHandler, pg.sprite.Sprite):
    """Menu osztály
    
    Az osztály tárolja a conténereket, kezeli az eventeket és azokat továbbítja
    a megfelelő containernek. A default container nem kiválasztható viszont
    ha nincs kiválasztva container annak továbbítódnak az eventek.
    
    Attributes:
        containers: containerek tárolására való lista
        focused: az a container amin az egérmutató áll, vagy ami előválasztott
            állapotban van
        default: a default container"""
    def __init__(self):
        """init metódus"""
        pg.sprite.Sprite.__init__(self)

        self.containers = pg.sprite.Group()

        self.focused = None
        self.selected = None
        self.default = None
        self.fixed = False

    def add(self, container: Container):
        """container hozzáadása a menü-höz
        
        Belső használatra mivel a container osztály nem hozható létre menu
        objektum megadása nélkül.
        """
        assert isinstance(container, Container), (f"Várt "
            f"pygame_menu.component.Container típus, kapott {type(container)}")
        
        #Az első container beállítása default-nak
        if len(self.containers) == 0:
            self.default = container
            container.default = True

        self.containers.add(container)

    def remove(self, container: Container):
        """container törlése
        
        Amennyiben az adott container-re már nincs szüksége. Default container
        törlésénél másik nem állítódik be."""

        if self.containers.has(container):
            if self.default == container:
                self.default = None
            self.containers.remove(container)

    def clear(self):
        """összes container törlése
        
        Ha egy menün belül szeretnénk váltogatni a container között, hasznos lehet."""
        self.focused = None
        self.selected = None
        self.default = None
        self.fixed = False
        self.containers.empty()

    def set_default(self, container: Container):
        """default container beállítása/lecserélése"""
        if self.default:
            self.default.default = False

        self.default = container
        container.default = True

    def lose_selection(self, container: Container):
        """a szelekciót elvesztő container osztály által meghívott metódus"""
        self.focused = None #container
        self.selected = None

        container.select = False
        container.focus = False #True

    #update és rajzolás

    def update(self):
        """containerek frissítése"""
        self.containers.update()

    def draw(self, surface : pg.Surface):
        """containerek rajzolása a kapott területre"""
        for container in self.containers:
            container.draw(surface)

    #eventkezelés - beviteli eszközök

    def get_rel_mouse_pos(self, item: Component, pos: tuple(int, int)) -> Pair:
        """relatív egér pozíció meghatározása
        
        Args:
            item: pygame_menu.component.Component objektum
            pos: az egérmutató pozíciója
            test: legyen-e tesztelve, hogy az egérmutató az item határain belül van-e

        Returns:
            utils.Pair objektum a relatív egér pozícióval
        """

        return Pair(pos) - item.position

    def is_mouse_in_item(self, item: Component, pos: tuple(int, int)) -> bool:
        """Megvizsgálja, hogy az egér az item határain belül van-e
        
        Args:
            item: pygame_menu.component.Component objektum
            pos: az egérmutató pozíciója
            
        Returns:
            bool érték"""
        rpos = self.get_rel_mouse_pos(item, pos)
        test = (rpos.p1 < 0 or rpos.p2 < 0 or rpos.p1 > item.area.width or
            rpos.p2 > item.area.height)

        return not test

    def get_focused(self, pos: tuple[int, int]) -> Component | None:
        """Az a komponens amin az egérmutató áll
        
        Args:
            pos: az egérmutató pozíciója
            
        Returns:
            Az egérmutatón álló komponens vagy None"""
        focused = None

        for container in self.containers:
            if self.is_mouse_in_item(container, pos):
                focused = container

        return focused

    #eventek - beviteli eszközök

    def e_MouseButtonDown(self, **kwargs):
        """egér gomblenyomás kezelése

        A componensnek a kwargs dict-et az in kulcsszóval kiegészítve küldi
        tovább. Az in azt jelzi a componensnek, hogy annak határain belül van-e
        a mutató.
        
        Args:
            kwargs: {pos, button, touch}"""
        # Csak az bal oldali gomb kezelése, a többi figyelmen kívül hagyása
        if kwargs['button'] != 1:
            return
        
        kwargs['in'] = True

        # Ha van kiválasztott component annak továbbadjuk a lekezelést
        if self.selected is not None:
            kwargs['in'] = self.is_mouse_in_item(self.selected, kwargs['pos'])
            kwargs['pos'] = self.get_rel_mouse_pos(self.selected, kwargs['pos'])
            self.selected.e_MouseButtonDown(**kwargs)

        # Ha rögzítve van a selected container
        if self.fixed:
            return

        # Ha van a mutató alatt component és az nem a jelenleg kiválasztott
        # component, akkor megváltoztatjuk a kiválasztást
        if self.focused is not None:
            if self.focused != self.selected:
                if self.selected is not None:
                    self.selected.select = False
                    self.selected = None
                # A default containert nem lehet kiválasztani
                if self.focused != self.default:
                    self.selected = self.focused
                    self.selected.select = True

                kwargs['in'] = self.is_mouse_in_item(self.focused, kwargs['pos'])
                kwargs['pos'] = self.get_rel_mouse_pos(self.focused, kwargs['pos'])
                self.focused.e_MouseButtonDown(**kwargs)
        # Ha az egér nem áll komponens fölött megszüntetjük a kiválasztást
        elif self.selected is not None:
            self.selected.select = False
            self.selected = None

    def e_MouseButtonUp(self, **kwargs):
        """egér gombelengedés kezelése

        A componensnek a kwargs dict-et az in kulcsszóval kiegészítve küldi
        tovább. Az in azt jelzi a componensnek, hogy annak határain belül van-e
        a mutató.
        
        Args:
            kwargs: {pos, button, touch}"""
        # Csak az bal oldali gomb kezelése, a többi figyelmen kívül hagyása
        if kwargs['button'] != 1:
            return
        
        kwargs['in'] = True

        # Ha volt kiválasztva container...
        if self.selected is not None:
            kwargs['in'] = self.is_mouse_in_item(self.selected, kwargs['pos'])
            kwargs['pos'] = self.get_rel_mouse_pos(self.selected, kwargs['pos'])
            self.selected.e_MouseButtonUp(**kwargs)
        # és ha nem, viszont a mutató a default containeren áll
        elif self.focused == self.default:
            kwargs['pos'] = self.get_rel_mouse_pos(self.default, kwargs['pos'])
            self.default.e_MouseButtonUp(**kwargs)

    def e_MouseMotion(self, **kwargs):
        """egér mozgás kezelése

        A componensnek a kwargs dict-et az in kulcsszóval kiegészítve küldi
        tovább. Az in azt jelzi a componensnek, hogy annak határain belül van-e
        a mutató.
        
        Args:
            kwargs: {pos, rel, button, touch}"""
        kwargs['in'] = True
        pos = kwargs['pos']

        # Ha van kiválasztott kontainer annak elküldjük az egér pozíciót.
        # Erre példáúl a scrollbar működéséhez van szükség
        if self.selected is not None:
            kwargs['in'] = self.is_mouse_in_item(self.selected, pos)
            kwargs['pos'] = self.get_rel_mouse_pos(self.selected, pos)
            self.selected.e_MouseMotion(**kwargs)

        # Ha rögzítve van a selected container
        if self.fixed:
            return

        # Az egérmutató alatt lévő containernek is elküldjük az egér pozícióját.
        focused = self.get_focused(pos)
        if focused is not None and focused != self.selected:
            kwargs['pos'] = self.get_rel_mouse_pos(focused, pos)
            focused.e_MouseMotion(**kwargs)
        
        # Ha a fókusz megváltozott azt lekezeljük
        if focused != self.focused:
            if self.focused is not None:
                self.focused.focus = False
            if focused is not None:
                focused.focus = True
            self.focused = focused

    def e_MouseWheel(self, **kwargs):
        """egér görgőjének továbbadása

        A mutató alatt lévő komponensnek adjuk tovább, vagy ha nincs ilyen akkor
        a kiválasztott komponensnek.
        
        Args:
            kwargs: {witch, flipped, x, y, touch}"""
        if self.focused is not None:
            self.focused.e_MouseWheel(**kwargs)
        elif self.selected is not None:
            self.selected.e_MouseWheel(**kwargs)

    def e_KeyDown(self, **kwargs):
        """billentyűzet gombnyomásának lekezelése

        Ha van kiválasztott componens akkor annak küldjük tovább az eseményt,
        ha nincs akkor vagy a fókuszban lévő komponensnek, vagy saját lekezelés
        történik.
        
        Args:
            kwargs: {key, mod, unicode, scancode}"""
        key = kwargs['key']

        # Ha van kiválasztott componens akkor annak küldjük az eseményt
        if self.selected is not None:
            self.selected.e_KeyDown(**kwargs)
        # Ha nincs akkor a TAB billentyűvel másik komponensre tesszük a fókuszt
        elif key == pg.K_TAB:
            # Megkeressük az jelenleg kiválasztoott container utáni első nem
            # default containert.
            first_container = None
            next_container = None
            next_is_good = False
            for container in self.containers:
                if first_container is None and container != self.default:
                    first_container = container
                if next_is_good and container != self.default:
                    next_container = container
                    break
                if container == self.focused:
                    next_is_good = True
            if next_container is None:
                next_container = first_container
            
            # Ha találtunk containert akkor annak átadjuk a fókuszt
            if next_container is not None:
                if self.focused is not None:
                    self.focused.focus = False
                self.focused = next_container
                self.focused.focus = True
        else:
            # Egyébként, ha a fókuszban lévő container nem a default akkor
            # azt kiválasztjuk
            if self.focused is not None and self.focused != self.default:
                self.selected = self.focused
                self.focused = None
                self.selected.select = True
            # Végűl ha nincs fókuszban componens és nincs kiválasztva sem akkor
            # az eseményt továbbítjuk a default-nak
            elif self.default is not None:
                self.default.e_KeyDown(**kwargs)

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése

        Ha van kiválasztott componens akkor annak küldjük tovább az eseményt,
        ha nincs akkor a default-nak.
        
        Args:
            kwargs: {key, mod, unicode, scancode}"""
        if self.selected is not None:
            self.selected.e_KeyUp(**kwargs)
        elif self.default is not None:
            self.default.e_KeyUp(**kwargs)

    # TODO: kontrollerről származó események kezelése
    # TODO: felbontás megváltoztatásának kezelése