import pygame as pg
from log_classes import SearchField, LogLevelSelector, LogList
import log_client as lc

pg.init()
lc.init()

screen = pg.display.set_mode([800,900], flags = pg.RESIZABLE)
canvas = pg.Surface((800,600))
items = pg.sprite.Group()
ll_selector = LogLevelSelector()
search_f = SearchField()
logs = LogList(search_f, ll_selector, lc.query)
items.add(ll_selector)
items.add(search_f)
items.add(logs)

font = pg.font.SysFont("Arial", 12)

mouse_pos = (0, 0)

running = True
while running:
    screen_size = screen.get_size()
    canvas = pg.Surface(screen_size)
    canvas.fill((0,40,20))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.MOUSEMOTION:
            mouse_pos = event.pos
        elif event.type == pg.MOUSEBUTTONDOWN and event.pos[1] < 15:
            ll_selector.e_MouseButtonDown(**event.__dict__)
        elif event.type == pg.MOUSEWHEEL and mouse_pos[1] < 15:
            ll_selector.e_MouseWheel(**event.__dict__)
        elif event.type == pg.MOUSEWHEEL:
            logs.e_MouseWheel(**event.__dict__)
        elif event.type == pg.WINDOWRESIZED:
            ll_selector.e_WindowResized(**event.__dict__)
            search_f.e_WindowResized(**event.__dict__)
            logs.e_WindowResized(**event.__dict__)
        elif event.type == pg.KEYDOWN:
            search_f.e_KeyDown(**event.__dict__)

    items.update()
    for item in items:
        if hasattr(item, 'area'):
            canvas.blit(item.image, item.rect, item.area)
        else:
            canvas.blit(item.image, item.rect)

    #for log in lc.query:
    #    print(log)
    #lc.query = []

    screen.blit(canvas, (0,0))

    pg.display.flip()

lc.stop()
pg.quit()