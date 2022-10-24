""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: editor_menu.py
Verzió: 1.0.0
--------------------
pygame_menu.menus.editor_menu

Pályaszerkesztő menü

Osztályok:
    EditroMenu
"""
from __future__ import annotations

import pygame as pg

from sokoban.data import loader
from sokoban.solver import festival
from utils import betweens
import sokoban.solver.solver as solver_utils
from sokoban import solver

from ..menu import Menu
from ..components import Container, Button, Label
from .containers import SelectContainer, TextEntryContainer

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainController
    from sokoban.editor import Editor

class EditorMenu(Menu):
    """Főmenü és játékslot választó

    Arguments:
        controller (MainController): legfelső vezérlő objektum
        screen (pygame.Surface): teljes megjelenítési felület
        editor (Editor): pályaszerkesztő osztály
        valid (bool): a pálya megoldható-e
        timeout (bool): a megoldó időtúllépése
        long_run (bool): a megoldó futhat 10 percig
        escape_down (bool): escape billentyű le lett-e nyomva
    """
    def __init__(self, controller: MainController, screen: pg.Surface, editor: Editor):
        """MainMenu

        Args:
            controller (MainController): legfelső vezérlő objektum
            screen (pygame.Surface): teljes megjelenítési felület
            editor (Editor): pályaszerkesztő osztály
        """
        Menu.__init__(self)

        self.controller = controller
        self.screen = screen

        self.editor = editor

        self.valid = False
        self.timeout = False
        self.long_run = False

        self.escape_down = False

        self.init_menu(None)

    def init_menu(self, _):
        """init_menu Pályaszerkesztő menü betöltése
        """
        self.clear()
        self.container = Container(self, size=(300,self.screen.get_size()[1]))

        self.container.color['bg'] = (0,0,0,180)
        self.container.color['focus'] = (0,0,0,180)
        self.container.color['select'] = (0,0,0,180)

        y_offset = 0
        if self.valid:
            self.button = Button(self.container, "Mentés", self.save_level, True, position=(1/8,1/16))
        else:
            self.button = Button(self.container, "Ellenőrzés", self.validate_level, True, position=(1/8,1/16))
        y_offset += self.button.size[1]
        b = Button(self.container, "Pályaméret...", self.show_level_size, position=(1/8,1/16+y_offset))

        Button(self.container, "Vissza", self.back, position=(1/8,13/16))
        Button(self.container, "Kilépés", self.exit_editor, position=(1/8,14/16))

        self.error_line_1 = Label(self.container, "", position=(1/16, 5/16))
        self.error_line_1.color['font'] = (255,100,100,255)
        self.error_line_2 = Label(self.container, "", position=(1/16, 6/16))
        self.error_line_2.color['font'] = (255,100,100,255)
        self.error_line_3 = Label(self.container, "", position=(1/16, 7/16))
        self.error_line_3.color['font'] = (255,100,100,255)
        #self.error_line_1.show = False

    def validate_level(self, _):
        """validate_level Pálya ellenőrzése
        """
        self.error_line_1.text = ""
        self.error_line_1.color['font'] = (255,100,100,255)
        self.error_line_2.text = ""
        self.error_line_3.text = ""

        if self.timeout:
            SelectContainer(self, "A pálya megoldása akár tíz percet is igánybe veget. Folytatja?",
                self.select_long_run)
            if not self.long_run:
                self.valid = True
                self.button.text = "Mentés"
                self.button.action = self.save_level
                return

        str_layout = festival.space_to_level_str(self.editor.space)
        solver_utils.initialize(str_layout, True)
        state = solver_utils.getState(str_layout, False, True)
        if state == 'MorePlayer':
            self.error_line_1.text = "Csak egy játékos"
            self.error_line_2.text = "lehet a pályán!"
            return
        elif state == 'NotEqualBoxGoal':
            self.error_line_1.text = "A dobozok és a"
            self.error_line_2.text = "célhelyek száma nem"
            self.error_line_3.text = "azonos!"
            return
        elif state == 'NoPlayer':
            self.error_line_1.text = "Játékosnak lennie"
            self.error_line_2.text = "kell a pályán!"
            return

        ret = solver_utils.validate(state[0], state[1])
        if ret == 'NotClosed':
            self.error_line_1.text = "A játéktér nem"
            self.error_line_2.text = "zárt!"
            return
        elif ret == 'NotReachableBoxGoal':
            self.error_line_1.text = "Van olyan doboz vagy"
            self.error_line_2.text = "célhely ami nem"
            self.error_line_3.text = "elérhető a játékossal!"
            return

        solver_utils.setFloors(self.editor.space, state[0])
        self.editor.space.init_level_data(self.editor.space.raw)

        timeout = 60
        if self.timeout:
            timeout = 600
        solverThread = solver.SolverThread(self.editor.space, self.set_solution, timeout, self.set_timeout)
        solverThread.start()

        solverThread.join()

        if self.timeout:
            self.error_line_1.text = "A pályát nem sikerült"
            self.error_line_2.text = f"{int(self.timeout/60)} perc alatt megoldani!"
            self.error_line_3.text = "Próbálja újra!"
            return
        if not self.valid:
            self.error_line_1.text = "A pálya megoldhatatlan!"
            return

        self.error_line_1.text = "A pálya rendben van!"
        self.error_line_1.color['font'] = (100,255,100,255)

        self.valid = True
        self.button.text = "Mentés"
        self.button.action = self.save_level

    def set_solution(self, solution):
        """set_solution Megoldás beállítása
        """
        if solution is None or solution == '':
            self.valid = False
            return

        self.valid = True

    def set_timeout(self, timeout):
        """set_timeout Időtúllépés beállítása
        """
        self.timeout = timeout

    def select_long_run(self, long_run):
        """select_long_run Hosszú (10 perces) megoldó futás beállítása

        Args:
            long_run (_type_): _description_
        """
        self.long_run = long_run

    def save_level(self, _):
        """save_level Pálya elmentése
        """
        loader.jset_data(self.editor.level, self.editor.space.raw, self.editor.set_name)

        self.error_line_1.text = "A pálya elmentve!"
        self.error_line_1.color['font'] = (100,255,100,255)

    def show_level_size(self, _):
        """show_level_size Pályaméretbeállító betöltése
        """
        tec = TextEntryContainer(self, "Pályaméret", self.set_level_size, position=(0,1/3), size=self.screen.get_size())
        tec.text_entry.value = f"{self.editor.space.size.p1}x{self.editor.space.size.p2}"

    def set_level_size(self, s):
        """set_level_size Pályaméret beállítása
        """
        if s is None:
            return

        size = s.split("x")
        size = [int(x) for x in size]
        size[0] = betweens(size[0], 3, 100)
        size[1] = betweens(size[1], 3, 100)

        self.editor.space.reshape(size[0], size[1])

    def back(self, _):
        """back Visszalépés a pályaszerkesztőbe
        """
        self.controller.resume_editor(self.editor, self)

    def exit_editor(self, _):
        """exit_editor Kilépés a pályaszerkesztőből
        """
        self.controller.exit_editor(self.editor.set_name, self.editor.level)

    def e_KeyDown(self, **kwargs):
        """billentyűzet gombnyomásának lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a lenyomott billentyű unicode értéke
            scancode (int?): a lenyomott billenytű scancode értéke"""
        super().e_KeyDown(**kwargs)

        if kwargs['key'] == pg.K_ESCAPE:
            self.escape_down = True

    def e_KeyUp(self, **kwargs):
        """billentyűzet gombfelengedésének lekezelése
        
        Kwargs:
            key (int): a billentyű kódja
            mod (int): módosítóbillentyűk
            unicode (char): a felengedett billentyű unicode értéke
            scancode (int?): a felengedett billenytű scancode értéke"""
        super().e_KeyUp(**kwargs)

        if kwargs['key'] == pg.K_ESCAPE and self.escape_down:
            self.back(None)