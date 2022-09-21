"""Sprite képek betöltése és kezelése

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
    loop (list[bool]): az adott képben lévő képkockák ismétlése ha szükséges"""
import pygame as pg
import json

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
            self.data = data["framesets"]

        self.load_images()        
        self.load_frameset()
        del(self, data)

    def load_images(self):
        """Képek betöltése
        """
        for frameset in self.data:
            if 'images' not in self.data[frameset]:
                continue
            for img_path in self.data[frameset]['images']:
                if img_path not in self.images:
                    self.images[img_path] = pg.image.load(f"{config.SKIN_PATH}{config.skin_name}/{img_path}").convert_alpha()

    def load_frameset(self):
        """Képkockák betöltése
        """
        for frameset in self.data:
            if 'copy' in self.data[frameset]:
                if self.data[frameset]['copy'] in self.data:
                    self.copy_frameset(self.data[self.data[frameset]['copy']], self.data[frameset])
                else:
                    continue

            self.load_frames(frameset)
            self.frame[frameset] = -1

    def copy_frameset(self, from_fs: dict, to_fs: dict):
        """Képkocka másolása

        Args:
            from_fs (dict): ahonnan másoljuk
            to_fs (dict): ahova másoljuk
        """
        for data in from_fs:
            if data not in to_fs:
                to_fs[data] = from_fs[data]

    def load_frames(self, frameset_name: str):
        """Képkockák betöltése

        Args:
            frameset_name (str): képkocka neve
        """
        frameset = self.data[frameset_name]
        self.frames[frameset_name] = []
        for frame_i in range(0, max(frameset['frames'])):
            w, h = frameset['size']
            sprite = pg.Surface((w, h), pg.SRCALPHA)
            #sprite.set_colorkey((0,0,0))

            for image_i in range(0, len(frameset['images'])):
                frames = frameset['frames'][image_i]
                offset_m = frame_i % frames if frames > frame_i or frameset['loop'][image_i] else frames - 1

                way = frameset['way'][image_i]

                if way == 'left':
                    offset_m_xy = (offset_m * -1, 0)
                elif way == 'right':
                    offset_m_xy = (offset_m, 0)
                elif way == 'up':
                    offset_m_xy = (0, offset_m * -1)
                else:
                    offset_m_xy = (0, offset_m)
                
                x = frameset['start_pos'][image_i][0] + frameset['frame_size'][image_i][0] * offset_m_xy[0]
                y = frameset['start_pos'][image_i][1] + frameset['frame_size'][image_i][1] * offset_m_xy[1]
                image_offset = (frameset['frame_pos'][image_i][0], frameset['frame_pos'][image_i][1])

                sprite.blit(self.images[frameset['images'][image_i]], image_offset, (x, y, frameset['frame_size'][image_i][0], frameset['frame_size'][image_i][0]), pg.BLEND_ALPHA_SDL2)
            
            if self.size != (0, 0):
                sprite = pg.transform.scale(sprite, self.size)
            if 'rotate' in frameset:
                sprite = pg.transform.rotate(sprite, frameset['rotate'])
            self.frames[frameset_name].append(sprite)

    def get_next_frame(self, frameset_name: str) -> pg.Surface:
        """Bizonyos nevű képkockákból a következő

        Args:
            frameset_name (str): képkocka neve

        Returns:
            pygame.Surface: a következő képkocka
        """
        if (self.frame[frameset_name] + 1) >= len(self.frames[frameset_name]):
            self.frame[frameset_name] = 0
        else:
            self.frame[frameset_name] += 1

        return self.frames[frameset_name][self.frame[frameset_name]]

    def get_frame(self, frameset_name: str, i: int) -> pg.Surface:
        """Bizonyos nevű képkockából egy adott számú

        Args:
            frameset_name (str): képkocka neve
            i (int): képkocka száma

        Returns:
            pygame.Surface: adott számú képkocka
        """
        if i < 0 or i >= len(self.frames[frameset_name]):
            return None
        self.frame[frameset_name] = i
        return self.frames[frameset_name][i]

    def get_frame_count(self, frameset_name: str) -> int:
        """Bizonyos nevű képkockákból azok száma

        Args:
            frameset_name (str): képkocka neve

        Returns:
            int: képkockák száma
        """
        return len(self.frames[frameset_name])

    def is_a_frame(self, frameset_name: str) -> bool:
        """Bizonyos nevű képkockák ellenőrzése

        Args:
            frameset_name (str): képkocka neve

        Returns:
            bool: képkocka létetik-e
        """
        return frameset_name in self.frames

    def get_frame_time(sefl):
        pass