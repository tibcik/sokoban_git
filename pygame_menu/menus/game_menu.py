"""Játék közben megjelenő menü
"""
from __future__ import annotations

import pygame as pg

from utils.pair import Pair
from sokoban import config
from sokoban.data import saves, loader

from ..components.component import STICKY_DOWNLEFT
from ..menu import Menu
from ..components import Container, Button, Label

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController
    from sokoban import Game

class GameMenu(Menu):
    """Játék közben megjelenő menü

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        game (Game): játék objektum
        next_level (bool): a menü a pálya befejezáse miatt jelenik meg
        escape_down (bool): ESC billentyű le van nyomva
    """
    def __init__(self, controller: MainController, screen: pg.Surface, game: Game, next_level: bool = False):
        """GameMenu

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pg.Surface): teljes megjelenítési felület
            game (Game): játék objektum
            next_level (bool, optional): a menü a pálya befejezáse miatt jelenik meg. Defaults to False.
        """
        Menu.__init__(self)

        self.controller = controller
        self.screen = screen

        self.game = game
        self.next_level = next_level

        self.escape_down = False

        if self.next_level:
            self.init_next_level_menu(None)
        else:
            self.init_menu(None)

    def init_menu(self, _):
        """Játék közbeni menü megjelenítése
        """
        self.clear()
        size = Pair(self.screen.get_size())
        size[0] = 300
        self.main_container = Container(self, size=size)
        self.main_container.color = (0,0,0,168)

        level_stat = saves.get_level_statistic(self.game.set_name, self.game.level)
        
        if level_stat is None:
            level_stat = {'moves': 0, 'time': 0, 'best_moves': 0, 'best_time': 0}

        level_stat['moves'] += self.game.pool.current_move
        level_stat['time'] += self.game.elapsed_time

        time_formater = lambda x : "{:02d}:{:02d}".format(int(x / 60), int(x % 60))

        y_offset = 0
        l = Label(self.main_container, "Összes idő a pályán: " + time_formater(level_stat['time']), position=(10,1/8), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 10
        l = Label(self.main_container, f"Összes lépés a pályán: {level_stat['moves']}", position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 30
        l = Label(self.main_container, "Legjobb idő a pályán: " + time_formater(level_stat['best_time']), position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 10
        l = Label(self.main_container, f"Legjobb lépés a pályán: {level_stat['best_moves']}", position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)

        y_offset = 0
        b = Button(self.main_container, "Folytatás", self.continue_game, position=(10,12/16), selected=True)
        y_offset += b.size[1] + 10
        if self.game.show_solution:
            b = Button(self.main_container, "Megoldás elrejtése", self.show_solution, position=(12,12/16+y_offset))
        else:
            b = Button(self.main_container, "Megoldás mutatása", self.show_solution, position=(12,12/16+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Újrakezdés", self.restart_game, position=(10,12/16+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Kilépés a menübe", self.exit_to_menu, position=(10,12/16+y_offset))

    def continue_game(self, _):
        """Folytatás gomb lenyomására lefutó metódus
        """
        self.controller.continue_game(self.game, self)
        self.game.resume()

    def show_solution(self, _):
        """Megoldás gomb lenyomására lefutó metódus
        """
        self.controller.continue_game(self.game, self)
        self.game.run_solver()
        self.game.resume()

    def restart_game(self, _):
        """Újrakezdés gomb lenyomására lefutó metódus
        """
        saves.done_level(self.game.set_name, self.game.level, self.game.pool.current_move, self.game.elapsed_time, False)
        self.game.restart()
        self.controller.continue_game(self.game, self)

    def exit_to_menu(self, _):
        """Kilépés a menübe gomb lenyomására lefutó metódus
        """
        saves.done_level(self.game.set_name, self.game.level, self.game.pool.current_move, self.game.elapsed_time, False)
        self.controller.init_main_menu()

    def init_next_level_menu(self, _):
        """Pálya befejezésekor megjelenő menü
        """
        self.clear()
        size = Pair(self.screen.get_size())
        size[0] = 300
        self.main_container = Container(self, size=size)
        self.main_container.color = (0,0,0,168)

        level_stat = saves.get_level_statistic(self.game.set_name, self.game.level)

        time_formater = lambda x : "{:02d}:{:02d}".format(int(x / 60), int(x % 60))

        y_offset = 0
        l = Label(self.main_container, "Összes idő a pályán: " + time_formater(level_stat['time']), position=(10,1/8), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 10
        l = Label(self.main_container, f"Összes lépés a pályán: {level_stat['moves']}", position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 30
        l = Label(self.main_container, "Legjobb idő a pályán: " + time_formater(level_stat['best_time']), position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 10
        if self.game.elapsed_time == level_stat['best_time']:
            l = Label(self.main_container, "ÚJ LEGJOBB IDŐ!", position=(20,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
            y_offset += l.size[1] + 20
        l = Label(self.main_container, f"Legjobb lépés a pályán: {level_stat['best_moves']}", position=(10,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)
        y_offset += l.size[1] + 10
        if self.game.pool.current_move == level_stat['best_moves']:
            l = Label(self.main_container, "ÚJ LEGJOBB LÉPÉSSZÁM!", position=(20,1/8 + y_offset), font_size=config.SMALL_FONT_SIZE)

        y_offset = 0
        if (self.game.level + 1) == loader.jget_levels():
            l = Label(self.main_container, "ÖSSZES PÁLYA TELJESÍTVE!", position=(10,6/8), font_size=config.SMALL_FONT_SIZE, sticky=STICKY_DOWNLEFT)
            l.color['font'] = (255,0,0,255)
            y_offset = l.size[1] + 10
        else:
            b = Button(self.main_container, "Következő szint", self.to_next_level, position=(10,6/8), selected=True)
            y_offset = b.size[1] + 10
        b = Button(self.main_container, "Újrakezdés", self.next_restart_game, position=(10,6/8+y_offset))
        y_offset += b.size[1] + 10
        b = Button(self.main_container, "Kilépés a menübe", self.next_exit_to_menu, position=(10,6/8+y_offset))

    def to_next_level(self, _):
        """Következő gomb lenyomására lefutó metódus
        """
        self.game.next_level()
        self.controller.continue_game(self.game, self)

    def next_restart_game(self, _):
        """Újrakezdés gomb lenyomására lefutó metódus
        """
        self.game.restart()
        self.controller.continue_game(self.game, self)

    def next_exit_to_menu(self, _):
        """Kilépés a menübe gomb lenyomására lefutó metódus
        """
        self.controller.init_main_menu()

    def e_KeyDown(self, **kwargs):
        """billentyűzet gombnyomásának lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a lenyomott billentyű unicode értéke
            scancode (int?): a lenyomott billenytű scancode értéke"""
        super().e_KeyDown(**kwargs)

        if kwargs['key'] == pg.K_ESCAPE and not self.next_level:
            self.escape_down = True

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        super().e_KeyUp(**kwargs)

        if kwargs['key'] == pg.K_ESCAPE and self.escape_down and not self.next_level:
            self.continue_game(None)