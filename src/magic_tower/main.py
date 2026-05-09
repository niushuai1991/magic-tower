import sys
import os
import pygame

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from magic_tower.sprites import SpriteManager
from magic_tower.game import GameState
from magic_tower.renderer import Renderer
from magic_tower.player import try_move, check_floor_transition
from magic_tower.battle import execute_battle, preview_battle
from magic_tower.save_load import save_game, load_game, has_save
from magic_tower.audio import AudioSystem
from magic_tower.interaction import (
    ichicheck, ichicheck2, get_msg, get_altar_options,
    execute_altar, execute_buy, execute_sell, execute_score,
)
from magic_tower.items import use_item
from magic_tower.object_data import MESSAGES

MOVE_DELAY_INITIAL = 8
MOVE_DELAY_REPEAT = 4


class MagicTowerApp:
    def __init__(self):
        pygame.init()
        self.screen_w = 820
        self.screen_h = 520
        self.screen = pygame.display.set_mode(
            (self.screen_w, self.screen_h), pygame.RESIZABLE
        )
        pygame.display.set_caption("Magic Tower")

        self.sprites = SpriteManager()
        self.renderer = Renderer(self.sprites)
        self.renderer.init_fonts()

        self.game = None
        self.state = "title"
        self.running = True
        self.message_text = None
        self.status_text = None
        self.battle_result = None
        self.move_timer = 0
        self.held_keys = set()

        self.altar_cursor = 1
        self.yesno_cursor = 1
        self.yesno_callback = None
        self.yesno_question = None
        self.pending_obj_info = None
        self.item_use_slot = None
        self.shake_timer = 0
        self.flash_timer = 0
        self.audio = AudioSystem()
        self.opening_page = 0
        self.opening_alpha = 0
        self.opening_fade_in = True

    def new_game(self):
        self.game = GameState()
        self.game.load_initial_maps()
        self.state = "playing"
        self.message_text = None
        self.status_text = "Welcome to Magic Tower!"
        self.battle_result = None
        self.audio.init()
        self.audio.play_bgm_for_floor(1)

    def run(self):
        self.sprites.load_all()

        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen_w = max(event.w, 410)
                    self.screen_h = max(event.h, 260)
                    self.screen = pygame.display.set_mode(
                        (self.screen_w, self.screen_h), pygame.RESIZABLE
                    )
                elif event.type == pygame.KEYDOWN:
                    self.held_keys.add(event.key)
                    self._handle_key_down(event.key)
                elif event.type == pygame.KEYUP:
                    self.held_keys.discard(event.key)

            if self.game and (self.game.move_ox or self.game.move_oy):
                self._animate_movement()

            self._render()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    def _render(self):
        if self.state == "title":
            self.renderer.render_title(self.screen)
        elif self.state == "opening":
            if self.opening_fade_in and self.opening_alpha < 255:
                self.opening_alpha = min(255, self.opening_alpha + 8)
                if self.opening_alpha >= 255:
                    self.opening_fade_in = False
            self.renderer.render_opening(
                self.screen, self.sprites, self.opening_page, self.opening_alpha
            )
        elif self.state in ("playing", "altar_menu", "yesno"):
            self.renderer.render_frame(
                self.screen, self.game, self.battle_result,
                self.message_text, self.status_text,
                shake=self.shake_timer, flash=self.flash_timer,
            )
            if self.shake_timer > 0:
                self.shake_timer -= 1
            if self.flash_timer > 0:
                self.flash_timer -= 1
            if self.state == "altar_menu":
                self.renderer.render_altar_menu(
                    self.screen, self.game, self.altar_cursor
                )
            elif self.state == "yesno":
                self.renderer.render_yesno(
                    self.screen, self.game, self.yesno_question, self.yesno_cursor
                )
        elif self.state == "game_over":
            self.renderer.render_game_over(self.screen)
        elif self.state in ("save_menu", "load_menu"):
            self._draw_menu()

    def _get_direction(self, key):
        if key in (pygame.K_UP, pygame.K_w, pygame.K_KP8):
            return 8
        if key in (pygame.K_DOWN, pygame.K_s, pygame.K_KP2):
            return 2
        if key in (pygame.K_LEFT, pygame.K_a, pygame.K_KP4):
            return 4
        if key in (pygame.K_RIGHT, pygame.K_d, pygame.K_KP6):
            return 6
        return None

    def _handle_key_down(self, key):
        if self.state == "title":
            if key == pygame.K_RETURN:
                if self.sprites.opening_imgs:
                    self.opening_page = 0
                    self.opening_alpha = 0
                    self.opening_fade_in = True
                    self.state = "opening"
                else:
                    self.new_game()
            elif pygame.K_1 <= key <= pygame.K_8:
                slot = key - pygame.K_0
                if has_save(slot):
                    self.game = GameState()
                    if load_game(self.game, slot):
                        self.state = "playing"
                        self.status_text = f"Loaded save {slot}"

        elif self.state == "opening":
            if key == pygame.K_ESCAPE:
                self.new_game()
            elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self.opening_page += 1
                self.opening_alpha = 0
                self.opening_fade_in = True
                if self.opening_page >= len(self.sprites.opening_imgs):
                    self.new_game()
        elif self.state == "altar_menu":
            self._handle_altar_key(key)
        elif self.state == "yesno":
            self._handle_yesno_key(key)
        elif self.state == "playing":
            self._handle_playing_key(key)
        elif self.state == "game_over":
            if key == pygame.K_r:
                self.new_game()
            elif key == pygame.K_ESCAPE:
                self.state = "title"
        elif self.state in ("save_menu", "load_menu"):
            self._handle_menu_key(key)

    def _handle_playing_key(self, key):
        if key == pygame.K_ESCAPE:
            self.state = "title"
            return
        if key == pygame.K_F5:
            self.state = "save_menu"
            return
        if key == pygame.K_F9:
            self.state = "load_menu"
            return
        if key == pygame.K_F12:
            self.game.language = (self.game.language + 1) % 3
            lang_names = ["English", "Japanese", "Chinese"]
            self.status_text = f"Language: {lang_names[self.game.language]}"
            return

        if self.message_text:
            if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
                self.message_text = None
            return

        if key == pygame.K_RETURN:
            self._handle_enter()
            return

        if key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                    pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9):
            slot = key - pygame.K_1
            if slot < 15 and self.game.item_box[slot] != 0:
                self.item_use_slot = slot
                self.yesno_question = get_msg(self.game, 314)
                self.yesno_cursor = 1
                self.yesno_callback = self._do_item_use
                self.state = "yesno"
            return

        self.move_timer = MOVE_DELAY_INITIAL
        direction = self._get_direction(key)
        if direction:
            self._do_move(direction)

    def _handle_enter(self):
        from magic_tower.interaction import check_adjacent_npcs
        info = check_adjacent_npcs(self.game)
        if info is None:
            return

        kind = info[0]
        if kind == "npc":
            _, obj, attr, nx, ny = info
            msg_id = attr[ATR_STRING]
            lang = self.game.language
            if lang < 2 and msg_id in MESSAGES.get(lang, {}):
                self.message_text = MESSAGES[lang][msg_id]
        elif kind == "altar":
            self.altar_cursor = 1
            self.state = "altar_menu"
        elif kind == "buy":
            _, obj, attr, gx, gy = info
            msg_id = attr[ATR_STRING]
            lang = self.game.language
            self.pending_obj_info = (obj, gx, gy)
            self.yesno_question = MESSAGES.get(lang, {}).get(msg_id, "Buy?")
            self.yesno_cursor = 1
            self.yesno_callback = self._do_buy
            self.state = "yesno"
        elif kind == "sell":
            _, obj, attr, gx, gy = info
            msg_id = attr[ATR_STRING]
            lang = self.game.language
            self.pending_obj_info = (obj, gx, gy)
            self.yesno_question = MESSAGES.get(lang, {}).get(msg_id, "Sell?")
            self.yesno_cursor = 1
            self.yesno_callback = self._do_sell
            self.state = "yesno"
        elif kind == "score":
            _, obj, attr, gx, gy = info
            result = execute_score(self.game, obj, gx, gy)
            self.message_text = result

    def _handle_altar_key(self, key):
        if key == pygame.K_UP:
            self.altar_cursor = max(1, self.altar_cursor - 1)
        elif key == pygame.K_DOWN:
            self.altar_cursor = min(5, self.altar_cursor + 1)
        elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            if self.altar_cursor == 5:
                self.state = "playing"
                return
            result = execute_altar(self.game, self.altar_cursor)
            if result:
                self.message_text = result
            self.state = "playing"
        elif key == pygame.K_ESCAPE:
            self.state = "playing"

    def _handle_yesno_key(self, key):
        if key == pygame.K_LEFT:
            self.yesno_cursor = 1
        elif key == pygame.K_RIGHT:
            self.yesno_cursor = 2
        elif key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_z):
            if self.yesno_cursor == 1 and self.yesno_callback:
                self.yesno_callback()
            self.state = "playing"
            if self.message_text is None:
                self.status_text = ""
        elif key == pygame.K_ESCAPE:
            self.state = "playing"

    def _do_buy(self):
        if self.pending_obj_info:
            obj, gx, gy = self.pending_obj_info
            result = execute_buy(self.game, obj, gx, gy)
            self.message_text = result
            self.audio.play_sfx(7)
            self.pending_obj_info = None

    def _do_sell(self):
        if self.pending_obj_info:
            obj, gx, gy = self.pending_obj_info
            result = execute_sell(self.game, obj, gx, gy)
            self.message_text = result
            self.audio.play_sfx(7)
            self.pending_obj_info = None

    def _do_item_use(self):
        if self.item_use_slot is not None:
            result = use_item(self.game, self.item_use_slot)
            if result:
                self.message_text = str(result)
            self.item_use_slot = None

    def _animate_movement(self):
        g = self.game
        speed = 10
        if g.move_ox > 0:
            g.move_ox = max(0, g.move_ox - speed)
        elif g.move_ox < 0:
            g.move_ox = min(0, g.move_ox + speed)
        if g.move_oy > 0:
            g.move_oy = max(0, g.move_oy - speed)
        elif g.move_oy < 0:
            g.move_oy = min(0, g.move_oy + speed)

    def _handle_menu_key(self, key):
        if key == pygame.K_ESCAPE:
            self.state = "playing"
        elif pygame.K_1 <= key <= pygame.K_8:
            slot = key - pygame.K_0
            if self.state == "save_menu":
                save_game(self.game, slot)
                self.status_text = f"Saved to slot {slot}"
                self.state = "playing"
            else:
                if has_save(slot):
                    self.game = GameState()
                    if load_game(self.game, slot):
                        self.state = "playing"
                        self.status_text = f"Loaded save {slot}"

    def _handle_held_keys(self):
        if self.message_text or self.state != "playing":
            return

        if self.move_timer > 0:
            self.move_timer -= 1
            return

        for key in self.held_keys:
            direction = self._get_direction(key)
            if direction:
                self.move_timer = MOVE_DELAY_REPEAT
                self._do_move(direction)
                break

    def _do_move(self, direction):
        result = try_move(self.game, direction)
        if result == "moved":
            self.battle_result = None
            self.audio.play_sfx(4)
            dx_map = {8: 0, 2: 0, 4: 1, 6: -1}
            dy_map = {8: 1, 2: -1, 4: 0, 6: 0}
            self.game.move_ox = dx_map[direction] * 40
            self.game.move_oy = dy_map[direction] * 40
            new_floor = check_floor_transition(self.game)
            if new_floor:
                self.status_text = f"Floor {new_floor}F"
                self.battle_result = None
                self.audio.play_sfx(8)
                self.audio.play_bgm_for_floor(new_floor)
                self.game.move_ox = 0
                self.game.move_oy = 0

            npc_msg = ichicheck(self.game)
            if npc_msg:
                self.status_text = npc_msg

            trap = ichicheck2(self.game)
            if trap:
                self.status_text = get_msg(self.game, trap["msg_id"])
                if self.game.game_over:
                    self.state = "game_over"
                    return

        elif isinstance(result, tuple):
            if result[0] == "battle":
                _, obj, obj_attr, gx, gy = result
                preview = preview_battle(self.game, obj_attr)
                if preview and not preview.get("can_attack", False):
                    self.status_text = "Can't attack! Too weak."
                    self.game.chara_x -= {8: 0, 2: 0, 4: -5, 6: 5}[direction]
                    self.game.chara_y -= {8: -5, 2: 5, 4: 0, 6: 0}[direction]
                    return
                battle = execute_battle(self.game, obj, obj_attr, gx, gy)
                if battle:
                    self.battle_result = battle
                    dmg = battle.get("player_damage", 0)
                    self.status_text = f"Battle! DMG taken: {dmg}"
                    self.shake_timer = 8
                    self.flash_timer = 6
                    self.audio.play_sfx(10)
                if self.game.game_over:
                    self.state = "game_over"

            elif result[0] == "message":
                _, msg_id = result
                lang = self.game.language
                if lang < 2 and msg_id in MESSAGES.get(lang, {}):
                    self.message_text = MESSAGES[lang][msg_id]
                self.status_text = ""

            elif result[0] == "altar":
                _, obj, attr, gx, gy = result
                self.altar_cursor = 1
                self.state = "altar_menu"

            elif result[0] == "buy":
                _, obj, attr, gx, gy = result
                msg_id = attr[ATR_STRING]
                lang = self.game.language
                self.pending_obj_info = (obj, gx, gy)
                self.yesno_question = MESSAGES.get(lang, {}).get(msg_id, "Buy?")
                self.yesno_cursor = 1
                self.yesno_callback = self._do_buy
                self.state = "yesno"

            elif result[0] == "sell":
                _, obj, attr, gx, gy = result
                msg_id = attr[ATR_STRING]
                lang = self.game.language
                self.pending_obj_info = (obj, gx, gy)
                self.yesno_question = MESSAGES.get(lang, {}).get(msg_id, "Sell?")
                self.yesno_cursor = 1
                self.yesno_callback = self._do_sell
                self.state = "yesno"

            elif result[0] == "score":
                _, obj, attr, gx, gy = result
                r = execute_score(self.game, obj, gx, gy)
                self.message_text = r

    def _draw_menu(self):
        w, h = self.screen.get_size()
        buf = pygame.Surface((820, 520))
        buf.fill((0, 0, 0))

        is_save = self.state == "save_menu"
        title = "Save Game" if is_save else "Load Game"
        if self.renderer.font_large:
            txt = self.renderer.font_large.render(title, True, (255, 255, 255))
            buf.blit(txt, (360, 100))
            for i in range(1, 9):
                exists = has_save(i)
                label = f"  {i}. Slot {i}" + (" [EXISTS]" if exists else " [EMPTY]")
                color = (200, 255, 200) if exists else (150, 150, 150)
                t = self.renderer.font.render(label, True, color)
                buf.blit(t, (300, 160 + (i - 1) * 35))
            esc = self.renderer.font.render("ESC to cancel", True, (180, 180, 180))
            buf.blit(esc, (340, 460))

        scaled = pygame.transform.smoothscale(buf, (w, h))
        self.screen.blit(scaled, (0, 0))


from magic_tower.game import ATR_STRING


def main():
    app = MagicTowerApp()
    app.run()


if __name__ == "__main__":
    main()
