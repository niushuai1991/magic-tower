from .game import ATR_TYPE, ATR_STRING, ATR_GOLD, ATR_ENERGY, ATR_CROP1
from .object_data import OBJECT_ATTR, MESSAGES, MAP_ATTR
from .interaction import get_msg

EVENT_FLAG_KEY = (76, 126)
EVENT_STATE_KEY = (71, 127)
EVENT_3F_KEY = (73, 126)
EVENT_COUNTER_KEY = (74, 126)

ANIM_FRAMES = 16
ANIM_FRAME_MS = 400


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


def get_event_counter(game):
    return game.obj_data[EVENT_COUNTER_KEY[0]][EVENT_COUNTER_KEY[1]]


def set_event_counter(game, val):
    game.obj_data[EVENT_COUNTER_KEY[0]][EVENT_COUNTER_KEY[1]] = val


def check_3f_trigger(game):
    if game.chara_x % 5 != 0 or game.chara_y % 5 != 0:
        return False
    gx, gy = game.get_global_pos()
    if gx == 31 and gy == 9 and get_3f_flag(game) == 0:
        return True
    return False


def trigger_3f_event(game):
    set_3f_flag(game, 1)
    set_event_counter(game, 3)
    return get_msg(game, 10)


def poll_3f_events(game, message_active):
    if message_active:
        return None
    flag = get_3f_flag(game)
    if flag == 1:
        set_3f_flag(game, 2)
        return ("message", get_msg(game, 222))
    elif flag == 2:
        return ("madoushi_anim",)
    elif flag == 3:
        set_3f_flag(game, 4)
        return ("message", get_msg(game, 223))
    elif flag == 4:
        return ("teleport",)
    return None


def finish_madoushi_anim(game):
    gx, gy = game.get_global_pos()
    game.set_object(gx, gy - 1, 58)
    game.set_object(gx - 1, gy, 58)
    game.set_object(gx + 1, gy, 58)
    game.set_object(gx, gy + 1, 58)
    set_3f_flag(game, 3)


def finish_zeno_anim(game):
    gx, gy = game.get_global_pos()
    game.set_object(gx, gy, 57)


def finish_teleport(game):
    gx, gy = game.get_global_pos()
    game.set_map_tile(gx, gy, 116)
    game.set_object(gx, gy, 0)
    game.direction = 0
    set_3f_flag(game, 5)
    set_event_counter(game, 0)
    tile_attr = MAP_ATTR.get(116)
    if tile_attr:
        jx = tile_attr[16] if len(tile_attr) > 16 else 0
        jy = tile_attr[17] if len(tile_attr) > 17 else 0
        game.map_x = jx // 13
        game.map_y = jy // 13
        game.chara_x = (jx % 13) * 5
        game.chara_y = (jy % 13) * 5
    game.hp = 400
    game.attack = 10
    game.defense = 10
    return ("openning_anim",)


def poll_openning_events(game, message_active):
    if message_active:
        return None
    counter = get_event_counter(game)
    if counter == 0:
        set_event_counter(game, 6)
        return ("message", get_msg(game, 266))
    elif counter == 6:
        set_event_counter(game, 7)
        return ("message", get_msg(game, 2))
    elif counter == 7:
        set_event_counter(game, 8)
        return ("message", get_msg(game, 3))
    elif counter == 8:
        set_event_counter(game, 9)
        return ("openning_done",)
    return None


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

    return events


def handle_boss_kill(game, gx, gy, obj):
    floor = game.current_floor()
    if floor == 3:
        if obj in (5, 6, 7, 8):
            set_3f_flag(game, 2)
            return get_msg(game, 10)
    return None
