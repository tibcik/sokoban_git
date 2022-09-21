import sys
import pygame as pg

import pygame_menu.menus as menus
from pygame_menu.menus.game_menu import GameMenu
from sokoban.utils import FpsDisplay
from sokoban import Game

class MainController:
    def __init__(self, args):
        pg.init()

        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode([1024,800])
        self.fps_module = FpsDisplay(self.clock)

        self.running = True

        self.controllers = pg.sprite.Group()
        self.active_controller = None

        if '-editor' in args:
            menu = menus.EditorMainMenu(self, self.screen)
        elif '-debug' in args:
            menu = menus.MainMenu(self, self.screen)
        else:
            menu = menus.MainMenu(self, self.screen)
        self.controllers.add(menu)
        #rgame = Game(self, screen)
        #self.controllers.add(rgame)
        self.active_controller = menu

        self.game = None

        self.show = True

        self.selected_player_id = None

    def run(self):
        while self.running:
            self.clock.tick(30)
            self.screen.fill((100,100,100))

            for event in pg.event.get():
                self.event(event)

            self.update()

            pg.display.flip()

        pg.quit()

    def update(self):
        if not self.show:
            return
        self.controllers.update()
        for c in self.controllers:
            c.draw(self.screen)

        self.fps_module.draw(self.screen)

    def event(self, e):
        if e.type == pg.QUIT:
            self.running = False
        if not self.show:
            return
        self.active_controller.event(e)

    # Menus
    def init_main_menu(self):
        menu = menus.MainMenu(self, self.screen)
        self.change_controller(menu)

        return menu

    def init_player_menu(self, selected_player_id):
        menu = menus.PlayerMenu(self, self.screen, selected_player_id)
        self.change_controller(menu)

        return menu

    def init_game(self, set_name, level):
        game = Game(self, self.screen, set_name, level)
        self.change_controller(game)

    def init_game_menu(self, game, next_level):
        menu = GameMenu(self, self.screen, game, next_level)
        self.add_controller(menu)

    def continue_game(self, game, menu):
        self.remove_controller(game, menu)

    # END

    def add_controller(self, controller):
        self.controllers.add(controller)
        self.active_controller = controller
    
    def remove_controller(self, new_controller, controller):
        self.controllers.remove(controller)
        self.active_controller = new_controller

    def change_controller(self, controller):
        self.controllers.empty()
        self.controllers.add(controller)
        self.active_controller = controller

    def exit(self, _):
        self.running = False

if __name__ == '__main__':
    mc = MainController(sys.argv)
    mc.run()