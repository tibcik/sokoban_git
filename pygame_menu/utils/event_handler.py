""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: event_handler.py
Verzió: 1.0.0
--------------------
pygame_menu.utils.event_handler

A pygame Event objektumát fogadó és azt lekezelő ősosztály tartalmazó modul

A fejlesztés segítése céljából az osztály tartalmazza a lehetséges pygame
eventeket mint metódusok és logolja azokat az eventeket amik nem illeszthetőek
egyik metódusra sem.
Egy másik funkció amit ellát pedig regisztrálja a gomblenyomásokat és azok
felengedését a billentyűzeten, egéren és controlleren így segítve a nyomva
tartott gombok felismerését az abból eredő események lekezelésének a lehetőségét.

Osztályok:
    EventHandler
"""
import pygame as pg

class EventHandler:
    """A pygame Event objektumát fogadó és azt lekezelő ősosztály tartalmazó modul

    A fejlesztés segítése céljából az osztály tartalmazza a lehetséges pygame
    eventeket mint metódusok és logolja azokat az eventeket amik nem illeszthetőek
    egyik metódusra sem.
    Egy másik funkció amit ellát pedig regisztrálja a gomblenyomásokat és azok
    felengedését a billentyűzeten, egéren és controlleren így segítve a nyomva
    tartott gombok felismerését az abból eredő események lekezelésének a lehetőségét.

    Mivel az osztály nem rendelkezik inicializáló metódussal ezért az osztály
    adattagjai property-ként vannak megvalósítva.

    Attributes:
        pge_pressed_keys(property): a billentyűzeten nyomvatartott gombok adatai
        pge_mouse_pressed_keys(property): az egéren nyomvatartott gombok adatai
        pge_joy_pressed_keys(property): a controlleren nyomvatartott gombok adatai
        pge_mouse_leaved(property): az egér elhagyta az ablakot
    """

    @property
    def pge_pressed_keys(self):
        if not hasattr(self, "_pge_pressed_keys"):
            self._pge_pressed_keys = []
        
        return self._pge_pressed_keys

    @property
    def pge_mouse_pressed_keys(self):
        if not hasattr(self, "_pge_mouse_pressed_keys"):
            self._pge_mouse_pressed_keys = []

        return self._pge_mouse_pressed_keys

    @property
    def pge_joy_pressed_keys(self):
        if not hasattr(self, "_pge_joy_pressed_keys"):
            self._pge_joy_pressed_keys = []

        return self._pge_joy_pressed_keys

    @property
    def pge_mouse_leaved(self):
        if not hasattr(self, "_pge_mouse_leaved"):
            self._pge_mouse_leaved = False

        return self._pge_mouse_leaved

    @pge_mouse_leaved.setter
    def pge_mouse_leaved(self, value):
        assert type(value) == bool, f"Várt bool típus, kapott {type(value)}"

        self._pge_mouse_leaved = value

    def event(self, e: pg.event.Event):
        """Event lekezelhetőségének vizsgálata és továbbküldése a lekezelőnek
        
        Args:
            e: pygame.event.Event objektum"""
        # assert isinstance(e, pg.event.Event), f"Várt pg.event.Event, kapott {type(e)}" TODO: ez itt miért nem jó?
        name = pg.event.event_name(e.type)

        if not hasattr(self, f"e_{name}"):
            name = "Unknown"

        self._registerKeyPress(e)
        self._registerKeyRelease(e)

        getattr(self, f"e_{name}")(**e.__dict__)

    def _registerKeyPress(self, e: pg.event.Event):
        """Gomblenyomás adatainak hozzáadása a megfelelő listához"""
        if e.type == pg.KEYDOWN:
            self.pge_pressed_keys.append(e.__dict__)
        elif e.type == pg.MOUSEBUTTONDOWN:
            self.pge_mouse_pressed_keys.append(e.__dict__)
        elif e.type == pg.JOYBUTTONDOWN:
            self.pge_joy_pressed_keys.append(e.__dict__)
    
    def _registerKeyRelease(self, e: pg.event.Event):
        key_list = None
        if e.type == pg.KEYUP:
            key_list = []
            for i in range(len(self.pge_pressed_keys)):
                if self.pge_pressed_keys[i]['key'] != e.key:
                    key_list.append(self.pge_pressed_keys[i])
            self.pge_pressed_keys.clear()
            self.pge_pressed_keys.extend(key_list)
        elif e.type == pg.MOUSEBUTTONUP:
            key_list = []
            for i in range(len(self.pge_mouse_pressed_keys)):
                if self.pge_mouse_pressed_keys[i]['button'] != e.button:
                    key_list.append(self.pge_pressed_keys[i])
            self.pge_mouse_pressed_keys.clear()
            self.pge_mouse_pressed_keys.extend(key_list)
        elif e.type == pg.JOYBUTTONUP:
            pass # TODO: később implementálni

    def _handleMouseMove(self, e: pg.event.Event):
        """Egér mozgásából adódó hiba lekezelése
        
        Ha egy egér gomb le van nyomva és a mutató elhagyja az ablakot az egér
        gomb felengedését nem regisztrálja a pygame. Amikor a mutató visszatér
        az ablak területére megvizsgáljuk az aktuálisan lenyomott gombokat."""
        if e.type == pg.WINDOWLEAVE:
            self.pge_mouse_leaved = True
        elif e.type == pg.MOUSEMOTION and self.isMouseLeaved() and self.isMouseKeyPressed():
            new_list = []
            for i in range(len(self.pge_mouse_pressed_keys)):
                pressed_button = self.pge_mouse_pressed_keys[i]['button']
                # A bal, középső, jobb gombokon kívűl a többi gombnyomás elvetése
                if pressed_button < 1 or pressed_button > 3:
                    continue
                if e.buttons[pressed_button - 1]:
                    new_list.append(self.pge_mouse_pressed_keys[i])
                # Az elengedett billentyűk elengedésének szimulálása
                else:
                    mouse_button_up = pg.event.Event(pg.MOUSEBUTTONUP, self.pge_mouse_pressed_keys[i])
                    self.event(mouse_button_up)

                self.pge_mouse_pressed_keys.clear()
                self.pge_mouse_pressed_keys.extend(new_list)
            self.pge_mouse_leaved = False

    def isKeyPressed(self):
        if len(self.pge_pressed_keys) > 0:
            return True

        return False

    def isMouseKeyPressed(self):
        if len(self.pge_mouse_pressed_keys) > 0:
            return True

        return False

    def isJoyKeyPressed(self):
        if len(self.pge_joy_pressed_keys) > 0:
            return True

        return False

    def isMouseLeaved(self):
        return self.pge_mouse_leaved
    
    def e_Unknown(self, **e):
        """Ismeretlen esemény által meghívott metódus. A metódus argumentumai
        nem ismertek.
        """
        pass

    def e_Quit(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_ActiveEvent(self, **kwargs):
        """kwargs: {gain, state}"""
        pass

    def e_KeyDown(self, **kwargs):
        """kwargs: {key, mod, unicode, scancode}"""
        pass

    def e_KeyUp(self, **kwargs):
        """kwargs: {key, mod, unicde, scancode}"""
        pass

    def e_MouseMotion(self, **kwargs):
        """kwargs: {pos, rel, buttons, touch}"""
        pass

    def e_MouseButtonUp(self, **kwargs):
        """kwargs: {pos, button, touch}"""
        pass

    def e_MouseButtonDown(self, **kwargs):
        """kwargs: {pos, button, touch}"""
        pass

    def e_JoyAxisMotion(self, **kwargs):
        """kwargs: {instance_id, axis, value}"""
        pass

    def e_JoyBallMotion(self, **kwargs):
        """kwargs: {instance_id, ball, rel}"""
        pass

    def e_JoyHatMotion(self, **kwargs):
        """kwargs: {instance_id, hat, value}"""
        pass

    def e_JoyButtonUp(self, **kwargs):
        """kwargs: {instance_id, button}"""
        pass

    def e_JoyButtonDown(self, **kwargs):
        """kwargs: {instance_id, button}"""
        pass

    def e_VideoResize(self, **kwargs):
        """kwargs: {w, h}"""
        pass

    def e_VideoExpose(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_UserEvent(self, **kwargs):
        """kwargs: {code}"""
        pass

    def e_AudioDeviceAdder(self, **kwargs):
        """kwargs: {which, iscapture}"""
        pass

    def e_AudioDeviceRemoved(self, **kwargs):
        """kwargs: {which, iscapture}"""
        pass

    def e_FingerMotion(self, **kwargs):
        """kwargs: {touch_id, finger_id, x, y, dx, dy}"""
        pass

    def e_FingerDown(self, **kwargs):
        """kwargs: {touch_id, finger_id, x, y, dx, dy}"""
        pass

    def e_FingerUp(self, **kwargs):
        """kwargs: {touch_id, finger_id, x, y, dx, dy}"""
        pass

    def e_MouseWheel(self, **kwargs):
        """kwargs: {which, flipped, x, y, touch}"""
        pass

    def e_MultiGesture(self, **kwargs):
        """kwargs: {touch_id, x, y, pinched, rotated, num_fingers"""
        pass

    def e_TextEditing(self, **kwargs):
        """kwargs: {text, start, length}"""
        pass

    def e_TextInput(self, **kwargs):
        """kwargs: {text}"""
        pass

    def e_DropBegin(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_DropComplete(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_DropFile(self, **kwargs):
        """kwargs: {file}"""
        pass

    def e_DropText(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_MidiIn(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_MidiOut(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_ControllerDeviceAdded(self, **kwargs):
        """kwargs: {device_index}"""
        pass

    def e_JoyDeviceAdded(self, **kwargs):
        """kwargs: {device_index}"""
        pass

    def e_ControllerDeviceRemoved(self, **kwargs):
        """kwargs: {instance_id}"""
        pass

    def e_JoyDeviceRemoved(self, **kwargs):
        """kwargs: {instance_id}"""
        pass

    def e_ControllerDeviceRemapped(self, **kwargs):
        """kwargs: {instance_id}"""
        pass

    def e_WindowShown(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowHidden(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowExposed(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowMoved(self, **kwargs):
        """kwargs: {x, y}"""
        pass

    def e_WindowResized(self, **kwargs):
        """kwargs: {w, h}"""
        pass

    def e_WindowSizeChanged(self, **kwargs):
        """kwargs: {w, h}"""
        pass

    def e_WindowMinimized(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowMaximized(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowRestored(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowEnter(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowLeave(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowFocusGained(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowFocusLost(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowClose(self, **kwargs):
        """kwargs: {}"""
        pass

    def e_WindowTakeFocus(self):
        """kwargs: {}"""
        pass

    def e_WindowHitTest(self):
        """kwargs: {}"""
        pass