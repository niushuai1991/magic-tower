import os
import pygame
from .game import ATR_TYPE, ATR_STRING, ATR_GOLD, ATR_ENERGY, ATR_CROP1
from .object_data import OBJECT_ATTR, MESSAGES, MAP_ATTR
from .interaction import get_msg

EVENT_FLAG_KEY = (76, 126)
EVENT_STATE_KEY = (71, 127)
EVENT_3F_KEY = (73, 126)


def get_event_flag(game):
    return game.obj_data[EVENT_FLAG_KEY[0]][EVENT_FLAG_KEY[1]]


def set_event_flag(game, val):
    game.obj_data[EVENT_FLAG_KEY[0]][EVENT_FLAG_KEY[1]] = val


def get_event_state(game):
    return game.obj_data[EVENT_STATE_KEY[0]][EVENT_STATE_KEY[1]]


def set_event_state(game, val):
    game.obj_data[EVENT_STATE_KEY[0]][EVENT_STATE_KEY[1]] = val


def get_3f_flag(game):
    return game.obj_data[EVENT_3F_KEY[0]][EVENT_3F_KEY[1]]


def set_3f_flag(game, val):
    game.obj_data[EVENT_3F_KEY[0]][EVENT_3F_KEY[1]] = val


def handle_floor_events(game):
    floor = game.current_floor()
    gx, gy = game.get_global_pos()
    events = []

    if floor == 1 and get_3f_flag(game) == 0:
        event_flag = get_event_flag(game)
        if event_flag == 0:
            thief_obj = game.get_object(gx, gy)
            if thief_obj == 87:
                msg = get_msg(game, 4)
                if msg:
                    events.append(("message", msg))
                game.hp = 400
                game.attack = 10
                game.defense = 10
                game.gold = 0
                set_3f_flag(game, 1)

    if floor == 1:
        obj = game.get_object(gx, gy)
        if obj == 88:
            msg = get_msg(game, 17)
            if msg:
                events.append(("message", msg))

    if floor == 50:
        state = get_event_state(game)
        if state == 0 and game.get_object(123, 59) == 88:
            if gx == 123 and gy == 59:
                set_event_state(game, 1)
                events.append(("message", get_msg(game, 43)))

        for s in range(1, 12):
            if state == s and gx == 123 and gy == 59:
                msg_id = 43 + s
                msg = get_msg(game, msg_id)
                if msg:
                    events.append(("message", msg))
                set_event_state(game, s + 1)
                break

        if get_event_state(game) == 12:
            events.append(("ending",))

    obj = game.get_object(gx, gy)
    if obj and obj in OBJECT_ATTR:
        attr = OBJECT_ATTR[obj]
        obj_type = attr[ATR_TYPE]
        msg_id = attr[ATR_STRING]
        if obj_type == 1 and msg_id and msg_id in MESSAGES.get(game.language, {}):
            pass

    return events


def handle_death_reload(game):
    if game.game_over and not game.death_reload_pending:
        game.death_reload_pending = True
        return get_msg(game, 280)

    if game.death_reload_pending:
        for slot in range(1, 9):
            from .save_load import has_save, load_game
            if has_save(slot):
                game.load_initial_maps()
                load_game(game, slot)
                game.game_over = False
                game.death_reload_pending = False
                return True
        return False

    return None


def handle_boss_kill(game, gx, gy, obj):
    floor = game.current_floor()

    if floor == 3:
        if obj in (5, 6, 7, 8):
            set_3f_flag(game, 2)
            return get_msg(game, 10)

    return None
