import pygame
from .sprites import TILE_SIZE
from .game import MAP_WALL, ATR_CROP1, ATR_CROP2, ATR_TYPE, ATR_ENERGY, ATR_STRENGTH, ATR_DEFENCE, ATR_GOLD, ATR_STRING
from .object_data import OBJECT_ATTR, MAP_ATTR, MESSAGES

BASE_WIDTH = 820
BASE_HEIGHT = 520
PANEL_LEFT_W = 150
MAP_SIZE = 13
MAP_PX = MAP_SIZE * TILE_SIZE


class Renderer:
    def __init__(self, sprites):
        self.sprites = sprites
        self.font = None
        self.font_large = None
        self.font_small = None
        self.anim_tick = 0

    def init_fonts(self):
        self.font = pygame.font.SysFont("sans", 16)
        self.font_large = pygame.font.SysFont("sans", 20, bold=True)
        self.font_small = pygame.font.SysFont("sans", 13)

    def render_frame(self, surface, game, battle_result=None, message_text=None, status_text=None, shake=0, flash=0):
        self.anim_tick += 1
        w, h = surface.get_size()
        buf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        buf.fill((0, 0, 0))

        self._draw_map(buf, game)
        self._draw_character(buf, game)
        self._draw_left_panel(buf, game)
        self._draw_right_panel(buf, game, battle_result)

        if message_text:
            self._draw_message_box(buf, message_text)

        if status_text:
            self._draw_status_bar(buf, status_text)

        if flash > 0 and flash % 2 == 1:
            flash_overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            flash_overlay.fill((255, 255, 255, 120))
            buf.blit(flash_overlay, (0, 0))

        sx = 0
        sy = 0
        if shake > 0:
            import random
            sx = random.randint(-3, 3)
            sy = random.randint(-3, 3)

        scaled = pygame.transform.smoothscale(buf, (w, h))
        surface.blit(scaled, (sx, sy))

    def _draw_map(self, buf, game):
        base_gx = game.map_x * 13
        base_gy = game.map_y * 13

        for ly in range(13):
            for lx in range(13):
                gx = base_gx + lx
                gy = base_gy + ly
                px = PANEL_LEFT_W + lx * TILE_SIZE
                py = ly * TILE_SIZE

                tile = game.get_map_tile(gx, gy)
                self._draw_tile(buf, px, py, tile)

                obj = game.get_object(gx, gy)
                if obj:
                    self._draw_object(buf, px, py, obj)

    def _draw_tile(self, buf, px, py, tile):
        attr = MAP_ATTR.get(tile)
        if attr:
            crop_id = attr[ATR_CROP1]
            tile_surf = self.sprites.get_tile(crop_id)
            buf.blit(tile_surf, (px, py))
        else:
            pygame.draw.rect(buf, (0, 0, 0), (px, py, TILE_SIZE, TILE_SIZE))

    def _draw_object(self, buf, px, py, obj):
        attr = OBJECT_ATTR.get(obj)
        if attr is None:
            return
        frame = (self.anim_tick // 15) % 2
        if frame == 0:
            crop_id = attr[ATR_CROP1]
        else:
            crop_id = attr[ATR_CROP2] if attr[ATR_CROP2] else attr[ATR_CROP1]
        tile_surf = self.sprites.get_tile(crop_id)
        buf.blit(tile_surf, (px, py))

    def _draw_character(self, buf, game):
        lx, ly = game.get_local_pos()
        px = PANEL_LEFT_W + lx * TILE_SIZE + game.move_ox
        py = ly * TILE_SIZE + game.move_oy

        direction = game.direction
        if direction == 8:
            frame_idx = 0
        elif direction == 2:
            frame_idx = 2
        elif direction == 4:
            frame_idx = 4
        elif direction == 6:
            frame_idx = 6
        else:
            frame_idx = 2

        anim = (self.anim_tick // 8) % 2
        chara_surf = self.sprites.get_chara(frame_idx // 2, anim)
        buf.blit(chara_surf, (px, py))

    def _draw_left_panel(self, buf, game):
        panel = pygame.Surface((PANEL_LEFT_W, BASE_HEIGHT))
        panel.fill((32, 32, 32))

        if self.font_large:
            floor = game.current_floor()
            txt = self.font_large.render(f"Tower {floor}F", True, (255, 255, 255))
            panel.blit(txt, (10, 10))

            y = 45
            for label, value, color in [
                ("HP", game.hp, (255, 80, 80)),
                ("ATK", game.get_total_attack(), (255, 200, 80)),
                ("DEF", game.get_total_defense(), (80, 150, 255)),
                ("GOLD", game.gold, (255, 220, 50)),
            ]:
                lbl = self.font.render(label, True, (180, 180, 180))
                val = self.font.render(str(value), True, color)
                panel.blit(lbl, (10, y))
                panel.blit(val, (60, y))
                y += 25

            y += 10
            for label, count, color in [
                ("Yellow", game.yellow_keys, (255, 255, 0)),
                ("Blue", game.blue_keys, (100, 100, 255)),
                ("Red", game.red_keys, (255, 50, 50)),
            ]:
                lbl = self.font.render(f"{label} Key", True, color)
                val = self.font.render(str(count), True, (255, 255, 255))
                panel.blit(lbl, (10, y))
                panel.blit(val, (110, y))
                y += 22

            y += 15
            hdr = self.font.render("Items:", True, (200, 200, 200))
            panel.blit(hdr, (10, y))
            y += 22
            for i in range(15):
                if game.item_box[i]:
                    from .object_data import OBJECT_ATTR
                    attr = OBJECT_ATTR.get(game.item_box[i])
                    if attr:
                        msg_id = attr[ATR_STRING]
                        lang = game.language
                        if lang < 2 and msg_id in MESSAGES.get(lang, {}):
                            name = MESSAGES[lang][msg_id]
                        else:
                            name = f"Item {game.item_box[i]}"
                        itxt = self.font_small.render(f"[{i+1}] {name}", True, (180, 220, 180))
                        panel.blit(itxt, (10, y))
                        y += 18

        buf.blit(panel, (0, 0))

    def _draw_right_panel(self, buf, game, battle_result=None):
        rx = PANEL_LEFT_W + MAP_PX
        panel = pygame.Surface((BASE_WIDTH - rx, BASE_HEIGHT))
        panel.fill((32, 32, 32))

        if self.font:
            if game.weapon:
                from .object_data import OBJECT_ATTR
                attr = OBJECT_ATTR.get(game.weapon)
                if attr:
                    crop_id = attr[ATR_CROP1]
                    tile = self.sprites.get_tile(crop_id)
                    panel.blit(tile, (55, 10))
                    txt = self.font.render("WEAPON", True, (255, 255, 255))
                    panel.blit(txt, (30, 55))

            if game.shield:
                from .object_data import OBJECT_ATTR
                attr = OBJECT_ATTR.get(game.shield)
                if attr:
                    crop_id = attr[ATR_CROP1]
                    tile = self.sprites.get_tile(crop_id)
                    panel.blit(tile, (55, 75))
                    txt = self.font.render("SHIELD", True, (255, 255, 255))
                    panel.blit(txt, (30, 120))

            if battle_result:
                y = 150
                txt = self.font.render("Monster Info:", True, (255, 100, 100))
                panel.blit(txt, (10, y))
                y += 22
                for label, val in [
                    ("HP", battle_result.get("mon_hp", 0)),
                    ("ATK", battle_result.get("mon_atk", 0)),
                    ("DEF", battle_result.get("mon_def", 0)),
                ]:
                    t = self.font.render(f"{label}: {val}", True, (255, 200, 150))
                    panel.blit(t, (15, y))
                    y += 20
                if "player_damage" in battle_result:
                    t = self.font.render(f"Dmg: {battle_result['player_damage']}", True, (255, 100, 100))
                    panel.blit(t, (15, y))

        buf.blit(panel, (rx, 0))

    def _draw_message_box(self, buf, text):
        box_w = MAP_PX - 40
        box_h = 80
        box_x = PANEL_LEFT_W + 20
        box_y = BASE_HEIGHT - box_h - 20

        pygame.draw.rect(buf, (20, 20, 60), (box_x, box_y, box_w, box_h))
        pygame.draw.rect(buf, (100, 100, 200), (box_x, box_y, box_w, box_h), 2)

        if self.font:
            lines = self._wrap_text(text, self.font, box_w - 20)
            for i, line in enumerate(lines[:3]):
                txt = self.font.render(line, True, (255, 255, 255))
                buf.blit(txt, (box_x + 10, box_y + 10 + i * 22))

    def _draw_status_bar(self, buf, text):
        bar_y = BASE_HEIGHT - 20
        pygame.draw.rect(buf, (30, 30, 80), (0, bar_y, BASE_WIDTH, 20))
        if self.font_small:
            txt = self.font_small.render(text, True, (200, 200, 255))
            buf.blit(txt, (10, bar_y + 2))

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = current + " " + word if current else word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def render_title(self, surface):
        w, h = surface.get_size()
        buf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        buf.fill((0, 0, 0))

        if self.sprites.title_img:
            scaled_title = pygame.transform.smoothscale(
                self.sprites.title_img, (BASE_WIDTH, BASE_HEIGHT)
            )
            buf.blit(scaled_title, (0, 0))
        else:
            if self.font_large:
                txt = self.font_large.render("Magic Tower", True, (255, 255, 255))
                buf.blit(txt, (BASE_WIDTH // 2 - txt.get_width() // 2, 200))

        if self.font:
            prompt = self.font.render("Press ENTER to start", True, (200, 200, 200))
            buf.blit(prompt, (BASE_WIDTH // 2 - prompt.get_width() // 2, 450))

        scaled = pygame.transform.smoothscale(buf, (w, h))
        surface.blit(scaled, (0, 0))

    def render_opening(self, surface, sprites, page, alpha):
        w, h = surface.get_size()
        buf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        buf.fill((0, 0, 0))

        if page < len(sprites.opening_imgs):
            img = sprites.opening_imgs[page]
            scaled_img = pygame.transform.smoothscale(img, (BASE_WIDTH, BASE_HEIGHT))
            if alpha < 255:
                scaled_img.set_alpha(alpha)
            buf.blit(scaled_img, (0, 0))

        if self.font_small:
            hint = self.font_small.render("ENTER to continue / ESC to skip", True, (180, 180, 180))
            buf.blit(hint, (BASE_WIDTH // 2 - hint.get_width() // 2, BASE_HEIGHT - 25))

        scaled = pygame.transform.smoothscale(buf, (w, h))
        surface.blit(scaled, (0, 0))

    def render_game_over(self, surface):
        w, h = surface.get_size()
        buf = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        buf.fill((0, 0, 0))

        if self.font_large:
            txt = self.font_large.render("GAME OVER", True, (255, 50, 50))
            buf.blit(txt, (BASE_WIDTH // 2 - txt.get_width() // 2, 200))
            prompt = self.font.render("Press R to restart", True, (200, 200, 200))
            buf.blit(prompt, (BASE_WIDTH // 2 - prompt.get_width() // 2, 280))

        scaled = pygame.transform.smoothscale(buf, (w, h))
        surface.blit(scaled, (0, 0))

    def render_altar_menu(self, surface, game, cursor):
        w, h = surface.get_size()
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))

        from .interaction import get_altar_options, get_msg
        opts = get_altar_options(game)

        box_x = PANEL_LEFT_W + 50
        box_y = 80
        box_w = 420
        box_h = 240

        pygame.draw.rect(overlay, (0, 0, 0, 240), (box_x, box_y, box_w, box_h), border_radius=10)

        options = [
            get_msg(game, 208),
            f"{get_msg(game, 209)}{opts['hp_gain']}{get_msg(game, 210)} ({opts['cost']}G)",
            f"{get_msg(game, 211)}{opts['atk_gain']}{get_msg(game, 212)} ({opts['cost']}G)",
            f"{get_msg(game, 213)}{opts['def_gain']}{get_msg(game, 212)} ({opts['cost']}G)",
            get_msg(game, 214),
        ]

        if self.font:
            for i, opt in enumerate(options):
                y = box_y + 10 + i * 44
                if i + 1 == cursor:
                    pygame.draw.rect(overlay, (80, 80, 0, 200), (box_x + 4, y, box_w - 8, 40), border_radius=6)
                else:
                    pygame.draw.rect(overlay, (40, 40, 40, 180), (box_x + 4, y, box_w - 8, 40), border_radius=6)
                color = (255, 255, 100) if i + 1 == cursor else (220, 220, 220)
                txt = self.font.render(opt, True, color)
                overlay.blit(txt, (box_x + 14, y + 10))

        scaled = pygame.transform.smoothscale(overlay, (w, h))
        surface.blit(scaled, (0, 0))

    def render_yesno(self, surface, game, question, cursor):
        w, h = surface.get_size()
        overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))

        box_x = PANEL_LEFT_W + 30
        box_y = 120
        box_w = 460
        box_h = 120

        pygame.draw.rect(overlay, (0, 0, 0, 240), (box_x, box_y, box_w, box_h), border_radius=10)

        if self.font:
            lines = self._wrap_text(question or "", self.font, box_w - 30)
            for i, line in enumerate(lines[:3]):
                txt = self.font.render(line, True, (255, 255, 255))
                overlay.blit(txt, (box_x + 15, box_y + 15 + i * 22))

            yes_color = (255, 255, 100) if cursor == 1 else (180, 180, 180)
            no_color = (255, 255, 100) if cursor == 2 else (180, 180, 180)

            yes_txt = self.font_large.render("YES", True, yes_color)
            no_txt = self.font_large.render("NO", True, no_color)
            overlay.blit(yes_txt, (box_x + 100, box_y + box_h - 45))
            overlay.blit(no_txt, (box_x + 300, box_y + box_h - 45))

        scaled = pygame.transform.smoothscale(overlay, (w, h))
        surface.blit(scaled, (0, 0))
