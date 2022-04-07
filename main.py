import sys
import pygame as pg

import pygame_menu.menus as menus
from sokoban.utils import FpsDisplay

class MainController:
    def __init__(self, args):
        pg.init()

        self.clock = pg.time.Clock()
        self.screen = pg.display.set_mode([800,600])
        self.fps_module = FpsDisplay(self.clock)

        self.running = True

        self.controllers = pg.sprite.Group()
        self.active_controller = None

        if '-editor' in args:
            menu = menus.EditorMainMenu(self, self.screen)
        elif '-game' in args:
            menu = MainMenu(self, self.screen)
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
            self.clock.tick(120)
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

    # END

    def add_controller(self, controller):
        self.controllers.add(controller)
        self.active_controller = controller

    def change_active_controller(self, controller):
        self.active_controller = controller
    
    def remove_controller(self, new_controller, controller):
        self.controllers.remove(controller)
        self.active_controller = new_controller

    def change_controller(self, controller):
        self.controllers.empty()
        self.controllers.add(controller)
        self.active_controller = controller

    def init_game(self, set_name, level):
        self.game = Game(self, self.screen, set_name, level)
        self.controllers.add(self.game)
        self.active_controller = self.game

    def level_clear(self):
        pass

    def new_game(self, *args, **kwargs):
        self.show = False
        self.controllers.empty()
        
        menu = menus.GameSlotSelector(self, self.screen)
        self.controllers.add(menu)
        self.active_controller = menu
        """
        self.game = Game(self, self.screen, 'default2', 0)
        self.controllers.add(self.game)
        self.active_controller = self.game
        """
        self.show = True

    def show_next_level(self):
        self.show = False
        next_level_menu = NextLevelMenu(self, self.screen)
        self.controllers.add(next_level_menu)
        self.active_controller = next_level_menu
        self.show = True

    def next_level(self, *args, **kwargs):
        self.show = False
        self.game.next_level()
        self.controllers.empty()
        self.controllers.add(self.game)
        self.active_controller = self.game
        self.show = True

    def reload(self, *args, **kwargs):
        self.show = False
        self.game.reload()
        self.controllers.empty()
        self.controllers.add(self.game)
        self.active_controller = self.game
        self.show = True

    def exit_to_menu(self, *args, **kwargs):
        self.show = False
        self.game = None
        menu = MainMenu(self, self.screen)
        self.controllers.add(menu)
        #rgame = Game(self, screen)
        #self.controllers.add(rgame)
        self.active_controller = menu
        self.show = True

    def show_editor_overlay(self, editor):
        menu = menus.EditorOverlayMenu(self, self.screen, editor)
        self.add_controller(menu)

    def editor(self):
        pass

    def exit(self, _):
        self.running = False

if __name__ == '__main__':
    mc = MainController(sys.argv)
    mc.run()