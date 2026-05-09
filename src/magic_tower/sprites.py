import os
import pygame

_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")

TILE_SIZE = 40

MAP_FRAME = [
    [0, 40], [40, 40], [80, 40], [0, 80], [40, 80], [80, 80],
    [0, 120], [40, 120], [80, 120],
    [120, 40], [160, 40], [200, 40], [240, 40],
    [120, 80], [160, 80], [200, 80], [240, 80],
    [120, 120],
    [280, 40], [360, 40], [280, 80], [320, 80], [360, 80], [280, 120],
]


class SpriteManager:
    def __init__(self):
        self.tiles = {}
        self.door_frames = []
        self.key_images = {}
        self.right_panel1 = None
        self.right_panel2 = None
        self.left_panel = None
        self.yusya_img = None
        self.title_img = None
        self.chara_sheet = None
        self.opening_imgs = []
        self.sheet = None

    def load_all(self):
        sheet_path = os.path.join(_ASSETS_DIR, "image", "MTower.gif")
        self.sheet = pygame.image.load(sheet_path).convert_alpha()

        for i in range(8):
            self.tiles[i] = self._crop(i * 40 + 80, 0)

        crop_id = 8
        for frame in MAP_FRAME:
            self.tiles[crop_id] = self._crop(frame[0], frame[1])
            crop_id += 1

        from .object_data import OBJECT_ATTR, MAP_ATTR

        for tile_id in range(1, 200):
            attr = MAP_ATTR.get(tile_id)
            if attr:
                sx, sy = attr[6], attr[7]
                if sx or sy or tile_id == 118:
                    crop1 = attr[1]
                    if crop1 not in self.tiles:
                        self.tiles[crop1] = self._crop(sx, sy)

        for obj_id in range(1, 200):
            attr = OBJECT_ATTR.get(obj_id)
            if attr:
                sx, sy = attr[6], attr[7]
                if sx or sy:
                    crop1 = attr[1]
                    if crop1 not in self.tiles:
                        self.tiles[crop1] = self._crop(sx, sy)
                sx2, sy2 = attr[8], attr[9]
                if sx2 or sy2:
                    crop2 = attr[2]
                    if crop2 not in self.tiles:
                        self.tiles[crop2] = self._crop(sx2, sy2)

        for i in range(1, 11):
            path = os.path.join(_ASSETS_DIR, "image", f"door{i}.gif")
            if os.path.exists(path):
                self.door_frames.append(pygame.image.load(path).convert_alpha())

        for i, key in enumerate(["key1", "key2", "key3"]):
            path = os.path.join(_ASSETS_DIR, "image", f"{key}.gif")
            if os.path.exists(path):
                self.key_images[i] = pygame.image.load(path).convert_alpha()

        for name in ["right1", "right2"]:
            path = os.path.join(_ASSETS_DIR, "image", f"{name}.gif")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                if name == "right1":
                    self.right_panel1 = img
                else:
                    self.right_panel2 = img

        left_path = os.path.join(_ASSETS_DIR, "image", "left.gif")
        if os.path.exists(left_path):
            self.left_panel = pygame.image.load(left_path).convert_alpha()

        yusya_path = os.path.join(_ASSETS_DIR, "image", "yusya.gif")
        if os.path.exists(yusya_path):
            self.yusya_img = pygame.image.load(yusya_path).convert_alpha()

        title_path = os.path.join(_ASSETS_DIR, "image", "title.gif")
        if os.path.exists(title_path):
            self.title_img = pygame.image.load(title_path).convert_alpha()

        chara_path = os.path.join(_ASSETS_DIR, "image", "image.gif")
        if os.path.exists(chara_path):
            self.chara_sheet = pygame.image.load(chara_path).convert_alpha()

        for name in ["open2", "open3"]:
            path = os.path.join(_ASSETS_DIR, "data", f"{name}.gif")
            if os.path.exists(path):
                self.opening_imgs.append(pygame.image.load(path).convert_alpha())

        for i in range(1, 19):
            path = os.path.join(_ASSETS_DIR, "data2", f"edata{i:02d}.gif")
            if os.path.exists(path):
                self.opening_imgs.append(pygame.image.load(path).convert_alpha())

    def _crop(self, x, y):
        return self.sheet.subsurface(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)).copy()

    def get_tile(self, crop_id, frame=0):
        if crop_id in self.tiles:
            return self.tiles[crop_id]
        return self._create_placeholder()

    def get_chara(self, direction, frame):
        idx = direction * 2 + frame
        if idx < 8 and idx in self.tiles:
            return self.tiles[idx]
        return self._create_placeholder()

    def _create_placeholder(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((255, 0, 255, 128))
        return surf
