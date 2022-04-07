import pygame as pg
import json
import config

import log.log
logger = log.log.init("Framesets")

class Framesets:
    """
        Statikus és animált sprite-ok betöltését segítő osztály.
        Json meta fájl felépítése:
        {"framesets": {
                "frameset_name1": {
                    "images": ["image1.png", "image2.jpg"],
                    "size": [#width#,#height#],
                    "frame_size": [[#width#, #height#], [#width#, #height#]],
                    "start_pos": [[#x#, #y#], [#x#, #y#]],
                    "frame_pos": [[#x#, #y#], [#x#, #y#]],
                    "frames": [#count#, #count#],
                    "way": ["left|right|up|down", "left|right|up|down"],
                    "loop": [true|false, true|false]
                }...
            }
        }
    """
    def __init__(self, size = (0, 0)):
        self.size = size

        self.images = {}
        self.frames = {}
        self.frame = {}

        with open(f"./skins/{config.skin}/skin.json") as f: # Hibakezelés
            data = json.load(f)
            self.data = data["framesets"]

        self.load_images()        
        self.load_frameset()

    def load_images(self):
        for frameset in self.data:
            if 'images' not in self.data[frameset]:
                continue
            for img_path in self.data[frameset]['images']:
                if img_path not in self.images:
                    self.images[img_path] = pg.image.load(f"./skins/{config.skin}/{img_path}").convert_alpha()

    def load_frameset(self):
        for frameset in self.data:
            if 'copy' in self.data[frameset]:
                if self.data[frameset]['copy'] in self.frames:
                    self.frames[frameset] = self.frames[self.data[frameset]['copy']]
                    self.frame[frameset] = -1
            else:
                self.load_frames(frameset)
                self.frame[frameset] = -1

    def load_frames(self, frameset_name):
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
            self.frames[frameset_name].append(sprite)

    def get_next_frame(self, frameset_name):
        if (self.frame[frameset_name] + 1) >= len(self.frames[frameset_name]):
            self.frame[frameset_name] = 0
        else:
            self.frame[frameset_name] += 1

        return self.frames[frameset_name][self.frame[frameset_name]]

    def get_frame(self, frameset_name, i):
        if i < 0 or i >= len(self.frames[frameset_name]):
            return None
        self.frame[frameset_name] = i
        return self.frames[frameset_name][i]

    def get_frame_count(self, frameset_name):
        return len(self.frames[frameset_name])