from .game import OBJ_DOOR, OBJ_MONSTER, OBJ_KEY, OBJ_MESSAGE
from .game import OBJ_NORMAL, OBJ_ITEM, OBJ_ALTAR, OBJ_SCORE, OBJ_SELL, OBJ_BUY, OBJ_EQUIP
from .game import ATR_TYPE, ATR_CROP1, ATR_CROP2, ATR_STRING, ATR_ENERGY, ATR_STRENGTH
from .game import ATR_DEFENCE, ATR_GOLD, ATR_ITEM, ATR_NUMBER, ATR_MODE, ATR_JUMP_X, ATR_JUMP_Y


SPECIAL_WEAPONS = {
    14: "cross",
    66: "dragon_slayer",
    76: "dragon_slayer",
    84: "dragon_slayer",
    85: "dragon_slayer",
}


def _is_walkable(tile):
    from .object_data import MAP_ATTR
    attr = MAP_ATTR.get(tile)
    if attr is None:
        return True
    t = attr[ATR_TYPE]
    return t == 0 or t == 2


def try_move(game, direction):
    if game.chara_x % 5 != 0 or game.chara_y % 5 != 0:
        return "continue"

    gx, gy = game.get_global_pos()
    dx, dy = 0, 0
    if direction == 8:
        dy = -1
    elif direction == 2:
        dy = 1
    elif direction == 4:
        dx = -1
    elif direction == 6:
        dx = 1
    else:
        return None

    tgx = gx + dx
    tgy = gy + dy
    game.direction = direction

    tile = game.get_map_tile(tgx, tgy)
    if not _is_walkable(tile):
        return None

    obj = game.get_object(tgx, tgy)
    if obj != 0:
        from .object_data import OBJECT_ATTR
        obj_attr = OBJECT_ATTR.get(obj)
        if obj_attr is not None:
            result = _handle_object(game, obj, obj_attr, tgx, tgy)
            if result == "block":
                return None
            if isinstance(result, tuple):
                return result

    new_cx = game.chara_x + dx * 5
    new_cy = game.chara_y + dy * 5
    new_lx = new_cx // 5
    new_ly = new_cy // 5
    if new_lx < 0 or new_lx >= 13 or new_ly < 0 or new_ly >= 13:
        return None

    game.chara_x = new_cx
    game.chara_y = new_cy
    return "moved"


def _handle_object(game, obj, obj_attr, gx, gy):
    obj_type = obj_attr[ATR_TYPE]

    if obj_type == OBJ_MONSTER:
        return ("battle", obj, obj_attr, gx, gy)
    elif obj_type == OBJ_DOOR:
        return _handle_door(game, obj, obj_attr, gx, gy)
    elif obj_type == OBJ_KEY:
        return _handle_key(game, obj, obj_attr, gx, gy)
    elif obj_type == OBJ_ITEM:
        return _handle_item(game, obj, obj_attr, gx, gy)
    elif obj_type == OBJ_EQUIP:
        return _handle_equip(game, obj, obj_attr, gx, gy)
    elif obj_type == OBJ_MESSAGE:
        msg_id = obj_attr[ATR_STRING]
        return ("message", msg_id)
    elif obj_type == OBJ_ALTAR:
        return ("altar", obj, obj_attr, gx, gy)
    elif obj_type == OBJ_BUY:
        return ("buy", obj, obj_attr, gx, gy)
    elif obj_type == OBJ_SELL:
        return ("sell", obj, obj_attr, gx, gy)
    elif obj_type == OBJ_SCORE:
        return ("score", obj, obj_attr, gx, gy)
    elif obj_type == OBJ_NORMAL:
        return None
    return None


def _handle_door(game, obj, obj_attr, gx, gy):
    if obj == 2:
        if game.yellow_keys > 0:
            game.yellow_keys -= 1
            game.set_object(gx, gy, 0)
            return None
        return "block"
    elif obj == 4:
        if game.blue_keys > 0:
            game.blue_keys -= 1
            game.set_object(gx, gy, 0)
            return None
        return "block"
    elif obj == 27:
        if game.red_keys > 0:
            game.red_keys -= 1
            game.set_object(gx, gy, 0)
            return None
        return "block"
    elif obj == 38:
        return "block"
    return "block"


def _handle_key(game, obj, obj_attr, gx, gy):
    if obj == 1:
        game.yellow_keys += 1
    elif obj == 3:
        game.blue_keys += 1
    elif obj == 28:
        game.red_keys += 1
    game.set_object(gx, gy, 0)
    return None


def _handle_item(game, obj, obj_attr, gx, gy):
    if 0 < obj <= 15:
        game.item_box[obj - 1] = obj
    game.set_object(gx, gy, 0)
    return None


def _handle_equip(game, obj, obj_attr, gx, gy):
    atk_bonus = obj_attr[ATR_ENERGY] if len(obj_attr) > ATR_ENERGY else 0
    def_bonus = obj_attr[ATR_DEFENCE] if len(obj_attr) > ATR_DEFENCE else 0
    game.attack += atk_bonus
    game.defense += def_bonus

    if obj == 114:
        game.attack_double = 2
    elif obj == 182:
        game.double_gold = True

    if obj in (30, 31, 32, 33, 34, 35, 36, 37, 38, 39):
        game.weapon = obj
    elif obj in (66, 67, 68, 76, 77, 78, 80, 81, 82, 83, 84, 85):
        game.shield = obj

    game.set_object(gx, gy, 0)
    return None


def check_floor_transition(game):
    if game.chara_x % 5 != 0 or game.chara_y % 5 != 0:
        return None

    gx, gy = game.get_global_pos()
    tile = game.get_map_tile(gx, gy)

    from .object_data import MAP_ATTR
    attr = MAP_ATTR.get(tile)
    if attr is None:
        return None

    tile_type = attr[ATR_TYPE]
    if tile_type != 2:
        return None

    jx = attr[ATR_JUMP_X] if len(attr) > ATR_JUMP_X else 0
    jy = attr[ATR_JUMP_Y] if len(attr) > ATR_JUMP_Y else 0
    if jx == 0 and jy == 0:
        return None

    new_map_x = jx // 13
    new_map_y = jy // 13
    new_chara_x = (jx % 13) * 5
    new_chara_y = (jy % 13) * 5

    if new_map_x == game.map_x and new_map_y == game.map_y:
        return None

    old_floor = game.current_floor()
    game.map_x = new_map_x
    game.map_y = new_map_y
    game.chara_x = new_chara_x
    game.chara_y = new_chara_y

    new_floor = game.current_floor()
    if 0 < new_floor <= 50 and new_floor > game.highest_floor:
        game.highest_floor = new_floor

    return new_floor
