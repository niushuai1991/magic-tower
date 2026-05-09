from .game import ATR_ENERGY, ATR_STRENGTH, ATR_DEFENCE, ATR_GOLD, ATR_ITEM, ATR_CROP1, ATR_CROP2


def calc_battle(game, obj, obj_attr):
    player_atk = game.get_total_attack()
    player_def = game.get_total_defense()

    mon_hp = obj_attr[ATR_ENERGY]
    mon_atk = obj_attr[ATR_STRENGTH]
    mon_def = obj_attr[ATR_DEFENCE]
    mon_gold = obj_attr[ATR_GOLD]

    if player_atk <= mon_def:
        return None

    damage_to_mon = player_atk * game.attack_double - mon_def
    rounds = (mon_hp + damage_to_mon - 1) // damage_to_mon

    if mon_atk <= player_def:
        damage_to_player = 0
    else:
        damage_to_monster_per = mon_atk - player_def
        damage_to_player = damage_to_monster_per * (rounds - 1)

    return {
        "mon_hp": mon_hp,
        "mon_atk": mon_atk,
        "mon_def": mon_def,
        "mon_gold": mon_gold,
        "damage_to_mon": damage_to_mon,
        "rounds": rounds,
        "player_damage": damage_to_player,
        "can_win": game.hp > damage_to_player,
    }


def execute_battle(game, obj, obj_attr, gx, gy):
    result = calc_battle(game, obj, obj_attr)
    if result is None:
        return None

    game.hp -= result["player_damage"]
    if game.hp <= 0:
        game.hp = 0
        game.game_over = True
        return result

    gold_gain = result["mon_gold"]
    if game.double_gold:
        gold_gain *= 2
    game.gold += gold_gain

    replacement = obj_attr[ATR_ITEM]
    game.set_object(gx, gy, replacement)

    return result


def preview_battle(game, obj_attr):
    player_atk = game.get_total_attack()
    player_def = game.get_total_defense()
    mon_hp = obj_attr[ATR_ENERGY]
    mon_atk = obj_attr[ATR_STRENGTH]
    mon_def = obj_attr[ATR_DEFENCE]

    if player_atk <= mon_def:
        return {
            "mon_hp": mon_hp, "mon_atk": mon_atk, "mon_def": mon_def,
            "can_attack": False, "player_damage": -1,
        }

    damage_to_mon = player_atk * game.attack_double - mon_def
    rounds = (mon_hp + damage_to_mon - 1) // damage_to_mon

    if mon_atk <= player_def:
        damage_to_player = 0
    else:
        damage_to_player = (mon_atk - player_def) * (rounds - 1)

    return {
        "mon_hp": mon_hp, "mon_atk": mon_atk, "mon_def": mon_def,
        "can_attack": True, "player_damage": damage_to_player,
        "rounds": rounds,
    }
