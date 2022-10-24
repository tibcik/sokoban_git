""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: win_key_press.py
Verzió: 1.0.0
--------------------
sokoban.solver.win_key_press

Windows rendszeren billentyűzet gombnyomás imitálása a festival solver miatt.
Az eredeti kód innen lett másolva:
https://stackoverflow.com/questions/21545897/how-to-control-interactive-console-input-output-from-python-on-windows

Osztályok:
    CHAR_UNION
    KEY_EVENT_RECORD
    INPUT_UNION
    INPUT_RECORD

Metódusok:
    write_key_to_console
"""

from ctypes import *
import msvcrt
import os

# input event types
KEY_EVENT = 0x0001

# constants, flags
MAPVK_VK_TO_VSC = 0

KEY = '\t'

# structures
class CHAR_UNION(Union):
    _fields_ = [("UnicodeChar", c_wchar),
                ("AsciiChar", c_char)]

    def to_str(self):
        return ''


class KEY_EVENT_RECORD(Structure):
    _fields_ = [("bKeyDown", c_byte),
                ("pad2", c_byte),
                ("pad1", c_short),
                ("wRepeatCount", c_short),
                ("wVirtualKeyCode", c_short),
                ("wVirtualScanCode", c_short),
                ("uChar", CHAR_UNION),
                ("dwControlKeyState", c_int)]

    def to_str(self):
        return ''


class INPUT_UNION(Union):
    _fields_ = [("KeyEvent", KEY_EVENT_RECORD)]

    def to_str(self):
        return ''


class INPUT_RECORD(Structure):
    _fields_ = [("EventType", c_short),
                ("Event", INPUT_UNION)]

    def to_str(self):
        return ''


def write_key_to_console():
    fdcon = os.open('CONIN$', os.O_RDWR | os.O_BINARY)
    hcon = msvcrt.get_osfhandle(fdcon)

    li = INPUT_RECORD * 2
    list_input = li()

    ke = KEY_EVENT_RECORD()
    ke.bKeyDown = c_byte(1)
    ke.wRepeatCount = c_short(1)

    cnum = ord(KEY)
    ke.wVirtualKeyCode = windll.user32.VkKeyScanW(cnum)
    ke.wVirtualScanCode = c_short(windll.user32.MapVirtualKeyW(int(cnum),
                                                               MAPVK_VK_TO_VSC))
    ke.uChar.UnicodeChar = chr(cnum)#unichr(cnum)
    kc = INPUT_RECORD(KEY_EVENT)
    kc.Event.KeyEvent = ke
    list_input[0] = kc

    list_input[1] = list_input[0]
    list_input[1].Event.KeyEvent.bKeyDown = c_byte(0)

    events_written = c_int()
    ret = windll.kernel32.WriteConsoleInputW(hcon,
                                             list_input,
                                             2,
                                             byref(events_written))

    os.close(fdcon)

    return ret
