""" Miskolci Egyetem 
Gépészmérnöki és Informatika Kar
Általános Informatikai Intézeti Tanszék

SZAKDOLGOZAT

Téma: Sokoban, megoldóval és pályaszerkesztővel
Készítette: Varga Tibor
Neptunkód: SZO2SL
Szak: Mérnök Informatikus BsC

File: frameset.py
Verzió: 1.0.0
--------------------
sokoban.utils.frameset

Sprite képek betöltése és kezelése

TODO: Ez már megváltozott, frissíteni az aktuális felépítésre
A skint és json fájl tartalmazza, ennek felépítése:
{
    "framesets": {
        "(str[frame_name])": {
            "copy(optional)": (str)
            "images": (list[img_file_name]),
            "size": (list[int,int]),
            "frame_size": (list[list[int,int]]),
            "start_pos": (list[list[int,int]]),
            "frame_pos": (list[list[int,int]]),
            "frames": (list[int]),
            "way": (list[str]),
            "loop": (list[bool]),
        }...
}
    copy (str, optional): a frame alapját adó másik frame, ha létezik az alap frame infomációi felülírásra kerülnek
    image (list[str]): a képfájlok nevei ahonnan a frameket vesszük
    size (list[int,int]): a kép mérete
    frame_size (list[list[int,int]]): a frame-ek mérete az egyes képfájlokban
    start_pos (list[list[int,int]]): a frame-ek kezdőpozíciója a képfájlokban
    frame_pos (list[list[int,int]]): a képen lévő pozíció ahova a frame-et be kell illeszteni az egyes képfájlok szerint
    frames (list[int]): az egyes képfájlokban lévő képkockák száma
    way (list[str]): up|down|left|rigt a képkockák olvasási iránya
    loop (list[bool]): az adott képben lévő képkockák ismétlése ha szükséges
    
Objektumok:
    Frameset
"""
import pygame as pg
import json

import time

from sokoban import config

class Framesets:
    """Sprite képek betöltése és kezelése
    
    Arguments:
        size (tuple[int,int]): a játékhoz szükséges méret
        images (dict[pygame.Surface]): sprite képek
        frames (dict): a betöltött képkockák
        frame (dict): az egyes képkockák aktuális száma"""
    def __init__(self, size = (0, 0)):
        """Framesets

        Args:
            size (tuple, optional): a játékhoz szükséges méret. Defaults to (0, 0).
        """
        self.size = size

        self.images = {}
        self.frames = {}
        self.frame = {}

        with open(f"{config.SKIN_PATH}{config.skin_name}/skin.json") as f: # Hibakezelés
            data = json.load(f)
            self.data = data["images"]

        self.load_images()        
        self.load_frameset()
        del(self, data)

    def load_images(self):
        """Képek betöltése
        """
        for frameset in self.data:
            if 'sprite' not in self.data[frameset]:
                continue
            img_path = self.data[frameset]['sprite']
            if img_path not in self.images:
                self.images[img_path] = pg.image.load(f"{config.SKIN_PATH}{config.skin_name}/{img_path}").convert_alpha()

    def load_frameset(self):
        """Képkockák betöltése
        """
        for frameset in self.data:
            self.load_frames(frameset)
            self.frame[frameset] = -1

    def load_frames(self, frameset_name: str, data: None | dict = None):
        """Képkockák betöltése

        Args:
            frameset_name (str): képkocka neve
        """
        if data is not None:
            frameset = data
        else:
            frameset = self.data[frameset_name]

        if 'frames' not in frameset:
            frameset['frames'] = 1
        if 'times' not in frameset:
            frameset['times'] = 1
        loop = False if 'loop' not in frameset else frameset['loop']
        next_frameset = None if 'next' not in frameset else frameset['next']
        self.frames[frameset_name] = {'images': [], 'frame': 0, 'loop': loop, 'times': [], 'last_time': -1, 'next': next_frameset}
        for frame_num in range(0, frameset['frames']):
            w, h = frameset['size']
            sprite = pg.Surface((w, h), pg.SRCALPHA)
            #sprite.set_colorkey((0,0,0))

            x = frameset['frame_start_pos'][0] + frameset['size'][0] * frame_num
            y = frameset['frame_start_pos'][1]

            sprite.blit(self.images[frameset['sprite']], (0, 0), (x, y, frameset['size'][0], frameset['size'][1]), pg.BLEND_ALPHA_SDL2)

            if self.size != (0, 0):
                sprite = pg.transform.scale(sprite, self.size)
            if 'rotate' in frameset:
                sprite = pg.transform.rotate(sprite, frameset['rotate'])
            if 'y_mirror' in frameset:
                sprite = pg.transform.flip(sprite, False, True)
            if 'x_mirror' in frameset:
                sprite = pg.transform.flip(sprite, True, False)
            
            self.frames[frameset_name]['images'].append(sprite)
            if type(frameset['times']) == list:
                if frame_num >= len(frameset['times']):
                    self.frames[frameset_name]['times'].append(frameset['times'][-1])
                else:
                    self.frames[frameset_name]['times'].append(frameset['times'][frame_num])
            else:
                self.frames[frameset_name]['times'].append(frameset['times'])


        if 'like' in frameset:
            for similar_frameset in frameset['like']:
                self.copy_data(frameset, frameset['like'][similar_frameset])
                self.load_frames(similar_frameset, frameset['like'][similar_frameset])

    def copy_data(self, from_data: any, to_data: any):
        """copy_data Adatok átmásoláso egyik objektumból a másikba, a létezőket megtartva

        Args:
            from_data (any): másolandó objektum
            to_data (any): objektum amibe az adatokat másoljuk
        """
        for data in from_data:
            if data not in to_data:
                if data != 'like':
                    to_data[data] = from_data[data]

    def get_frame(self, frameset_name: str, reset = False, fast = False) -> pg.Surface:
        """Bizonyos nevű képkockákból a következő

        Args:
            frameset_name (str): képkocka neve

        Returns:
            pygame.Surface: a következő képkocka
        """
        data = self.frames[frameset_name]

        if len(data['images']) == 1:
            return (frameset_name, data['images'][0])

        if data['last_time'] == -1 or reset:
            return self.reset_frame(frameset_name)

        frame = data['frame']

        now = time.time()
        if frame == len(data['times']):
            if data['next']:
                if now - data['last_time'] > (data['times'][frame - 1] / (10 if fast else 1)):
                    data['last_time'] = -1
                    #self.frames[data['next']]['last_time'] = now
                    return self.reset_frame(data['next']) # (data['next'], self.frames[data['next']]['images'][0], 0)
                else:
                    return (frameset_name, None)
            elif data['loop']:
                if now - data['last_time'] > (data['times'][frame - 1] / (10 if fast else 1)):
                    self.reset_frame(frameset_name)
                    data['frame'] += 1
                    return (frameset_name, data['images'][0])
                else:
                    return (frameset_name, None)
            else:
                return (frameset_name, False)
        elif now - data['last_time'] > (data['times'][frame - 1]  / (10 if fast else 1)):
            data['frame'] += 1
            data['last_time'] = now
            return (frameset_name, data['images'][frame])
        else:
            return (frameset_name, None)

    def reset_frame(self, frameset_name: str) -> pg.Surface:
        """reset_frame Számláló és idő alaphelyzetbe állítása

        Args:
            frameset_name (str): az objektum neve

        Returns:
            pg.Surface: első képkocka
        """
        self.frames[frameset_name]['last_time'] = time.time()
        self.frames[frameset_name]['frame'] = 1

        return (frameset_name, self.frames[frameset_name]['images'][0])

    def get_frame_count(self, frameset_name: str) -> int:
        """Bizonyos nevű képkockákból azok száma

        Args:
            frameset_name (str): képkocka neve

        Returns:
            int: képkockák száma
        """
        return len(self.frames[frameset_name]['images'])

    def is_a_frame(self, frameset_name: str) -> bool:
        """Bizonyos nevű képkockák ellenőrzése

        Args:
            frameset_name (str): képkocka neve

        Returns:
            bool: képkocka létetik-e
        """
        return frameset_name in self.frames