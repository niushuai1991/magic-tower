from .game import ATR_GOLD, ATR_STRING, ATR_TYPE
from .object_data import OBJECT_ATTR, MESSAGES


def get_msg(game, msg_id):
    lang = game.language
    if lang < 2 and msg_id in MESSAGES.get(lang, {}):
        return MESSAGES[lang][msg_id]
    return ""


def check_adjacent_npcs(game):
    gx, gy = game.get_global_pos()
    dx_map = {8: (0, -1), 2: (0, 1), 4: (-1, 0), 6: (1, 0)}
    ddx, ddy = dx_map.get(game.direction, (0, -1))
    nx, ny = gx + ddx, gy + ddy
    obj = game.get_object(nx, ny)
    if obj == 0:
        return None

    attr = OBJECT_ATTR.get(obj)
    if attr is None:
        return None

    obj_type = attr[ATR_TYPE]

    if obj_type == 1:
        return ("npc", obj, attr, nx, ny)
    elif obj_type == 7:
        return ("altar", obj, attr, nx, ny)
    elif obj_type == 14:
        return ("sell", obj, attr, nx, ny)
    elif obj_type == 15:
        return ("buy", obj, attr, nx, ny)
    elif obj_type == 11:
        return ("score", obj, attr, nx, ny)

    return None


def ichicheck(game):
    gx, gy = game.get_global_pos()
    for ddx, ddy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = gx + ddx, gy + ddy
        obj = game.get_object(nx, ny)
        if obj == 0:
            continue
        attr = OBJECT_ATTR.get(obj)
        if attr is None:
            continue
        obj_type = attr[ATR_TYPE]

        if obj_type == 1:
            return get_msg(game, 144)
        elif obj_type == 7:
            return get_msg(game, 155)
        elif obj_type == 14 or obj_type == 15:
            return get_msg(game, 144)
        elif obj_type == 11:
            return get_msg(game, 144)
        elif obj_type == 0:
            if obj == 79:
                return get_msg(game, 183)

    return None


BOSS_EXCLUSIONS = {57, 58, 74, 50, 51, 52, 90, 91, 92, 93, 94, 102}
MAGICIAN_A = 99
MAGICIAN_B = 100
MAGIC_MASTER = 126
DRAGON = 119


def ichicheck2(game):
    gx, gy = game.get_global_pos()
    result = {"msg_id": 0, "hp_loss": 0, "death": False}

    up = game.get_object(gx, gy - 1)
    down = game.get_object(gx, gy + 1)
    left = game.get_object(gx - 1, gy)
    right = game.get_object(gx + 1, gy)

    if up == MAGICIAN_A or down == MAGICIAN_A or left == MAGICIAN_A or right == MAGICIAN_A:
        result["msg_id"] = 241
        result["hp_loss"] = 200

    if up == MAGICIAN_B or down == MAGICIAN_B or left == MAGICIAN_B or right == MAGICIAN_B:
        result["msg_id"] = 242
        result["hp_loss"] = 100

    if ((up == MAGIC_MASTER and down == MAGIC_MASTER) or
            (left == MAGIC_MASTER and right == MAGIC_MASTER)):
        result["msg_id"] = 243
        result["hp_loss"] = game.hp // 2

    if up == DRAGON:
        result["msg_id"] = 269
        result["hp_loss"] = 1000

    if result["hp_loss"] > 0:
        game.hp -= result["hp_loss"]
        if game.hp <= 0:
            game.hp = 0
            game.game_over = True
            result["death"] = True

    return result if result["msg_id"] else None


def get_altar_options(game):
    cost = (game.altar_count + 1) * 100
    hp_gain = (game.altar_count + 1) * 100
    atk_gain = game.map_y * 2 + 2
    def_gain = game.map_y * 4 + 4
    return {
        "cost": cost,
        "hp_gain": hp_gain,
        "atk_gain": atk_gain,
        "def_gain": def_gain,
    }


def execute_altar(game, choice):
    opts = get_altar_options(game)
    cost = opts["cost"]
    if game.gold < cost:
        return get_msg(game, 215)

    if choice == 1:
        game.hp += opts["hp_gain"]
    elif choice == 2:
        game.attack += opts["atk_gain"]
    elif choice == 3:
        game.defense += opts["def_gain"]
    else:
        return None

    game.gold -= cost
    game.altar_count += 1
    return get_msg(game, 283)


BUY_EFFECTS = {
    17: {"type": "yellow_key", "count": 1, "replace": 0},
    18: {"type": "blue_key", "count": 1, "replace": 40},
    41: {"type": "yellow_keys", "count": 5, "replace": 155},
    156: {"type": "red_key", "count": 1, "replace": 157},
    159: {"type": "blue_key", "count": 1, "replace": 160},
    162: {"type": "yellow_and_blue", "yellow": 4, "blue": 1, "replace": 163},
    164: {"type": "yellow_keys", "count": 3, "replace": 165},
    166: {"type": "blue_keys", "count": 3, "replace": 169},
    168: {"type": "hp", "count": 2000, "replace": 169},
    170: {"type": "super_mattock", "replace": 171},
}


def execute_buy(game, obj, gx, gy):
    attr = OBJECT_ATTR.get(obj)
    if attr is None:
        return get_msg(game, 18)

    cost = attr[ATR_GOLD]
    if game.gold < cost:
        return get_msg(game, 18)

    effect = BUY_EFFECTS.get(obj)
    if effect is None:
        return get_msg(game, 18)

    game.gold -= cost

    etype = effect["type"]
    if etype == "blue_key":
        game.blue_keys += 1
    elif etype == "yellow_key":
        game.yellow_keys += 1
    elif etype == "yellow_keys":
        game.yellow_keys += effect["count"]
    elif etype == "red_key":
        game.red_keys += 1
    elif etype == "blue_keys":
        game.blue_keys += effect["count"]
    elif etype == "yellow_and_blue":
        game.yellow_keys += effect["yellow"]
        game.blue_keys += effect["blue"]
    elif etype == "hp":
        game.hp += effect["count"]
    elif etype == "super_mattock":
        game.item_box[12] = 13

    if effect.get("replace", 0):
        game.set_object(gx, gy, effect["replace"])
    return get_msg(game, 98)


def execute_sell(game, obj, gx, gy):
    attr = OBJECT_ATTR.get(obj)
    if attr is None:
        return get_msg(game, 252)

    if game.yellow_keys <= 0:
        return get_msg(game, 252)

    price = attr[ATR_GOLD]
    game.yellow_keys -= 1
    game.gold += price
    game.hp += price
    return get_msg(game, 98)


def execute_score(game, obj, gx, gy):
    floor = game.current_floor()
    score = game.hp + game.get_total_attack() * 10 + game.get_total_defense() * 10
    score += game.gold
    msg = get_msg(game, 224)
    return f"{msg} Score: {score}"
