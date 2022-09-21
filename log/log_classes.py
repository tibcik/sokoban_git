import pygame as pg

class LogLevelSelector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.w_width = pg.display.get_window_size()[0]
        self.image = pg.Surface((0, 0))
        self.rect = pg.rect.Rect(0,0,0,0)

        self._level = self.w_width / 100 * 99

        self.listener = None

        self.updated = True

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value
        if self.w_width < value:
            self._level = self.w_width
        elif 0 > value:
            self._level = 0
        self.updated = True

    def update(self):
        if self.updated:
            self.update_image()
            self.updated = False

            if self.listener is not None:
                self.listener.updated = True

    def update_image(self):
        self.image = pg.Surface((self.w_width, 15))
        rate = 512 / self.w_width
        for i in range(self.w_width):
            r, g = 255, 255
            if i >= self.w_width / 2:
                g = min(255, (self.w_width - i) * rate)
            else:
                r = min(255, i * rate)
            pg.draw.line(self.image, (r, g, 0), (i, 0), (i, 15))
            if i == self.level:
                pg.draw.line(self.image, (0,0,0), (i, 0), (i, 15), 3)

    def e_MouseButtonDown(self, pos, button, *args, **kwargs):
        if button == 1:
            self.level =  pos[0]

    def e_MouseWheel(self, y, *args, **kwargs):
        if y < 0:
            self.level = self.level - round(self.w_width / 100)
        elif y > 0:
            self.level = self.level + round(self.w_width / 100)

    def e_WindowResized(self, x, *args, **kwargs):
        w_width = pg.display.get_window_size()[0]
        rate = w_width / self.w_width
        self.w_width = w_width
        self.level = round(self.level * rate)

    def add_listener(self, listener):
        self.listener = listener

class SearchField(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.font = pg.font.SysFont("Helvetica", 12) #TODO skin fájlban megadható

        self.w_width = pg.display.get_window_size()[0]
        self.image = pg.Surface((0,0))
        self.rect = pg.rect.Rect(0, 15, 0, 0)

        self.value = ""

        self.updated = True
        self.listener = None

        self.selectors = []

    def update(self):
        if self.updated:
            self.update_image()
            self.updated = False

    def update_image(self):
        self.image = pg.Surface((self.w_width, 32))
        self.image.fill((0,0,0))

        rfont = self.font.render(self.value, True, (255,255,0))
        self.image.blit(rfont, (3, 12))

    def set_selectors(self):
        self.selectors = self.value.split(",")
        if len(self.selectors) == 1 and self.selectors[0] == "":
            self.selectors = []
        if self.listener is not None:
            self.listener.updated = True

    def e_KeyDown(self, key, unicode, *args, **kwargs):
        if key == pg.K_BACKSPACE:
            self.value = self.value[0:-1]
        elif unicode != "":
            self.value += unicode

        self.updated = True
        self.set_selectors()

    def e_WindowResized(self, x, *args, **kwargs):
        self.w_width = pg.display.get_window_size()[0]
        
        self.updated = True

    def add_listener(self, listener):
        self.listener = listener

class LogList(pg.sprite.Sprite):
    def __init__(self, selector_field, leveller, query):
        super().__init__()

        self.sf = selector_field
        self.sf.add_listener(self)
        self.l = leveller
        self.query = query

        self.font = pg.font.SysFont("Helvetica", 22) #TODO skin fájlban megadható

        self.w_size = pg.display.get_window_size()
        self.image = pg.Surface((0, 0))
        self.rect = pg.rect.Rect(0, 47, 0, 0)
        self.area = pg.rect.Rect(0,0,0,0)
        self.area.size = self.w_size

        self.updated = True

    def update(self):
        if self.updated:
            self.update_image()
            self.updated = True

    def update_image(self):
        s = self.sf.selectors
        img_height = 6 + len(self.query) * 26
        self.image = pg.Surface((self.w_size[0], img_height))
        self.image.fill((0,30,10))
        line = 0
        for i in range(len(self.query)-1, 0, -1):
            log = self.query[i]
            if (self.l.level / self.w_size[0] * 100) < log.levelno:
                continue
            m_head = f"{log.filename} - {log.funcName} - {log.lineno}: "
            hide = True
            if len(s) == 0 or log.name in s or log.filename in s or log.filename in s or log.funcName in s:
                hide = False
            s_t = log.msg.split("::")
            if len(s_t) <= 1:
                text = m_head + log.msg
            else:
                text = m_head + s_t[1]
                selectors = s_t[0].split(",")
                for sel in selectors:
                    if sel in self.sf.selectors:
                        hide = False

            if hide:
                continue

            r = log.levelno * (255 / 50) if log.levelno < 50 else 255
            g = 255 if log.levelno < 50 else (100 - log.levelno) * (255 / 50)
            rtext = self.font.render(text, True, (r, g, 0))
            self.image.blit(rtext, (3, 6 + line * 26))

            line += 1

            #if 59 + (line) * 26 > self.w_size[1]:
            #    break

    def e_MouseWheel(self, y, *args, **kwargs):
        if y > 0:
            self.area.y -= 40
            if self.area.y < 0:
                self.area.y = 0
        elif y < 0:
            self.area.y += 40
            if self.area.y > (self.image.get_height() - self.w_size[1] - 47):
                self.area.y = self.image.get_height() - self.w_size[1] - 47

        self.updated = True

    def e_WindowResized(self, *args, **kwargs):
        self.w_size = pg.display.get_window_size()
        self.area.size = self.w_size

        self.updated = True