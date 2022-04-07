import pygame as pg

from .menu import Menu
from .components import *
from .sokoban_components import *

class TestMenu(Menu):
    def __init__(self, controller, screen):
        Menu.__init__(self)

        c = Container(self, position=(0,0), size=screen.get_size())
        Button(c, "Almalé", None, position=(1/8,1/12))
        Checkbox(c, position=(1/8,2/12))
        Label(c, "Répalé", position=(1/8,3/12))
        Select(c, ("alma", "répa", "retek", "mogyoró"), position=(1/8,4/12))
        TextEntry(c, position=(1/8,5/12), size=(120,32))
        MultiTextEntry(c, position=(1/8,6/12), size=(120,200))
        #Label(c, "Test", position=(1000,1000))