from .game import ATR_TYPE, ATR_ENERGY, ATR_DEFENCE, ATR_GOLD, OBJ_MONSTER


def use_item(game, slot):
    item = game.item_box[slot]
    if item == 0:
        return None

    if slot == 3:
        return _use_pickaxe(game)
    elif slot == 4:
        return _use_elixir(game)
    elif slot == 5:
        return _use_ice_wand(game)
    elif slot == 6:
        return _use_zapper(game)
    elif slot == 7:
        return _use_mirror(game)
    elif slot == 8:
        return _use_floor_up(game)
    elif slot == 9:
        return _use_floor_down(game)
    elif slot == 10:
        return _use_pickaxe(game)
    elif slot == 11:
        return _use_all_doors(game)
    elif slot == 12:
        return _use_iron_doors(game)

    return None


def _use_pickaxe(game):
    gx, gy = game.get_global_pos()
    broken = False
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = gx + dx, gy + dy
        tile = game.get_map_tile(nx, ny)
        if tile == 3:
            game.set_map_tile(nx, ny, 1)
            game.set_object(nx, ny, 0)
            broken = True
    if broken:
        game.item_box[3] = 0
        return "wall_broken"
    return None


def _use_elixir(game):
    hp_gain = game.attack * 10 + game.defense * 5
    game.hp += hp_gain
    game.item_box[3] = 0
    return f"heal_{hp_gain}"


def _use_ice_wand(game):
    gx, gy = game.get_global_pos()
    opened = False
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = gx + dx, gy + dy
        tile = game.get_map_tile(nx, ny)
        if tile == 3:
            game.set_map_tile(nx, ny, 1)
            opened = True
    if opened:
        game.item_box[5] = 0
        return "iron_door_opened"
    return None


def _use_zapper(game):
    gx, gy = game.get_global_pos()
    from .object_data import OBJECT_ATTR
    total_gold = 0
    killed = False
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = gx + dx, gy + dy
        obj = game.get_object(nx, ny)
        if obj == 0:
            continue
        attr = OBJECT_ATTR.get(obj)
        if attr and attr[ATR_TYPE] == OBJ_MONSTER:
            gold = attr[ATR_GOLD]
            if game.double_gold:
                gold *= 2
            total_gold += gold
            game.set_object(nx, ny, 0)
            killed = True
    if killed:
        game.gold += total_gold
        game.item_box[6] = 0
        return f"zapped_{total_gold}"
    return None


def _use_mirror(game):
    lx, ly = game.get_local_pos()
    mirror_lx = 12 - lx
    mirror_ly = 12 - ly

    mgx = game.map_x * 13 + mirror_lx
    mgy = game.map_y * 13 + mirror_ly

    target_obj = game.get_object(mgx, mgy)
    target_tile = game.get_map_tile(mgx, mgy)

    if target_obj != 0 or target_tile != 1:
        return "mirror_blocked"

    game.chara_x = mirror_lx * 5
    game.chara_y = mirror_ly * 5
    return "mirrored"


def _use_floor_up(game):
    floor = game.current_floor()
    if floor >= 50:
        return "no_floor"

    game.set_object(*game.get_global_pos(), game.direction)

    if game.map_x == 9:
        game.map_x = 0
        game.map_y += 1
    else:
        game.map_x += 1

    game.item_box[8] = 0
    new_floor = game.current_floor()
    if new_floor > game.highest_floor:
        game.highest_floor = new_floor
    return f"floor_{new_floor}"


def _use_floor_down(game):
    floor = game.current_floor()
    if floor <= 1:
        return "no_floor"

    if game.map_x == 0:
        game.map_x = 9
        game.map_y -= 1
    else:
        game.map_x -= 1

    game.item_box[9] = 0
    return f"floor_{game.current_floor()}"


def _use_all_doors(game):
    base_x = game.map_x * 13
    base_y = game.map_y * 13
    opened = False
    for ly in range(13):
        for lx in range(13):
            gx = base_x + lx
            gy = base_y + ly
            obj = game.get_object(gx, gy)
            if obj == 2:
                game.set_object(gx, gy, 0)
                opened = True
    if opened:
        game.item_box[11] = 0
        return "doors_opened"
    return None


def _use_iron_doors(game):
    base_x = game.map_x * 13
    base_y = game.map_y * 13
    opened = False
    for ly in range(13):
        for lx in range(13):
            gx = base_x + lx
            gy = base_y + ly
            tile = game.get_map_tile(gx, gy)
            if tile == 3:
                game.set_map_tile(gx, gy, 1)
                opened = True
    if opened:
        game.item_box[12] = 0
        return "iron_doors_opened"
    return None
