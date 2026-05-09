from .map_data import FLOOR_MAPS, FLOOR_OBJECTS

MAP_STREET = 0
MAP_WALL = 1
MAP_LOCALGATE = 2

OBJ_NORMAL = 0
OBJ_MESSAGE = 1
OBJ_EQUIP = 3
OBJ_ITEM = 4
OBJ_DOOR = 5
OBJ_MONSTER = 6
OBJ_ALTAR = 7
OBJ_KEY = 8
OBJ_SCORE = 11
OBJ_SELL = 14
OBJ_BUY = 15

ATR_CROP1 = 1
ATR_CROP2 = 2
ATR_TYPE = 3
ATR_MODE = 4
ATR_STRING = 5
ATR_ENERGY = 10
ATR_STRENGTH = 11
ATR_DEFENCE = 12
ATR_GOLD = 13
ATR_ITEM = 14
ATR_NUMBER = 15
ATR_JUMP_X = 16
ATR_JUMP_Y = 17


class GameState:
    def __init__(self):
        self.map_data = [[0] * 130 for _ in range(78)]
        self.obj_data = [[0] * 130 for _ in range(78)]

        self.chara_x = 30
        self.chara_y = 55
        self.map_x = 0
        self.map_y = 0
        self.direction = 8

        self.hp = 400
        self.attack = 10
        self.defense = 10
        self.gold = 0
        self.yellow_keys = 0
        self.blue_keys = 0
        self.red_keys = 0

        self.weapon = 0
        self.shield = 0
        self.item_slots = [0] * 15

        self.highest_floor = 1
        self.altar_count = 0
        self.event_counter = 0
        self.event_3f = 0

        self.language = 0
        self.sound_mode = 2
        self.bgm_mode = 0

        self.attack_double = 1
        self.double_gold = False

        self.item_box = [0] * 15
        self.chie_orb = [0] * 26
        self.chie_num = 0

        self.score = 0
        self.score2 = 0
        self.player_name = ""

        self.game_over = False
        self.game_won = False
        self.death_reload_pending = False
        self.move_ox = 0
        self.move_oy = 0

    def load_initial_maps(self):
        for gy in range(78):
            for gx in range(130):
                self.map_data[gy][gx] = 1
                self.obj_data[gy][gx] = 0

        for gy in range(78):
            for gx in range(130):
                if gy % 13 == 0:
                    if gx % 13 == 0:
                        self.map_data[gy][gx] = 30
                    elif gx % 13 == 12:
                        self.map_data[gy][gx] = 32
                    else:
                        self.map_data[gy][gx] = 31
                elif gy % 13 == 12:
                    if gx % 13 == 0:
                        self.map_data[gy][gx] = 35
                    elif gx % 13 == 12:
                        self.map_data[gy][gx] = 37
                    else:
                        self.map_data[gy][gx] = 36
                elif gx % 13 == 0:
                    self.map_data[gy][gx] = 33
                elif gx % 13 == 12:
                    self.map_data[gy][gx] = 34

        for floor_num in range(1, 51):
            if floor_num not in FLOOR_MAPS:
                continue
            my = (floor_num - 1) // 10
            mx = (floor_num - 1) % 10
            floor_map = FLOOR_MAPS[floor_num]
            floor_obj = FLOOR_OBJECTS[floor_num]
            for ly in range(13):
                for lx in range(13):
                    if ly == 0 or ly == 12 or lx == 0 or lx == 12:
                        continue
                    gy = my * 13 + ly
                    gx = mx * 13 + lx
                    if gy < 78 and gx < 130:
                        self.map_data[gy][gx] = floor_map[ly][lx]
                        self.obj_data[gy][gx] = floor_obj[ly][lx]

    def current_floor(self):
        return self.map_y * 10 + self.map_x + 1

    def get_local_pos(self):
        lx = self.chara_x // 5
        ly = self.chara_y // 5
        return lx, ly

    def get_global_pos(self):
        lx, ly = self.get_local_pos()
        return self.map_x * 13 + lx, self.map_y * 13 + ly

    def get_map_tile(self, gx, gy):
        if 0 <= gx < 130 and 0 <= gy < 78:
            return self.map_data[gy][gx]
        return MAP_WALL

    def get_object(self, gx, gy):
        if 0 <= gx < 130 and 0 <= gy < 78:
            return self.obj_data[gy][gx]
        return 0

    def set_map_tile(self, gx, gy, val):
        if 0 <= gx < 130 and 0 <= gy < 78:
            self.map_data[gy][gx] = val

    def set_object(self, gx, gy, val):
        if 0 <= gx < 130 and 0 <= gy < 78:
            self.obj_data[gy][gx] = val

    def get_total_attack(self):
        from .object_data import OBJECT_ATTR
        bonus = 0
        if self.weapon:
            attr = OBJECT_ATTR.get(self.weapon)
            if attr:
                bonus += attr[ATR_ENERGY]
        return self.attack + bonus

    def get_total_defense(self):
        from .object_data import OBJECT_ATTR
        bonus = 0
        if self.shield:
            attr = OBJECT_ATTR.get(self.shield)
            if attr:
                bonus += attr[ATR_ENERGY]
        return self.defense + bonus

    def to_save_data(self):
        data = []
        for y in range(78):
            row_m = []
            row_o = []
            for x in range(130):
                row_m.append(self.map_data[y][x])
                row_o.append(self.obj_data[y][x])
            data.append((row_m, row_o))

        self._set_hidden_state()
        return data

    def _set_hidden_state(self):
        self.obj_data[66][118] = self.hp
        self.obj_data[67][118] = self.attack
        self.obj_data[68][118] = self.defense
        self.obj_data[69][118] = self.gold
        self.obj_data[66][119] = self.altar_count
        self.obj_data[71][118] = self.highest_floor
        self.obj_data[74][118] = self.yellow_keys
        self.obj_data[75][118] = self.blue_keys
        self.obj_data[76][118] = self.red_keys
        self.obj_data[71][119] = self.weapon
        self.obj_data[72][119] = self.shield
        self.obj_data[70][124] = self.chara_x
        self.obj_data[71][124] = self.chara_y
        self.obj_data[72][124] = self.sound_mode
        self.obj_data[75][124] = self.bgm_mode
        self.obj_data[76][121] = self.language
        self.obj_data[74][126] = self.event_counter
        self.obj_data[73][126] = self.event_3f
        self.obj_data[69][119] = 0
        self.obj_data[70][119] = 0
        self.obj_data[66][120] = 1 if self.attack_double > 1 else 0
        self.obj_data[67][120] = 1 if self.double_gold else 0
        for i in range(15):
            if i < 6:
                row = 71 + i
                col = 119
            else:
                row = 66 + (i - 6)
                col = 120
            self.obj_data[row][col] = self.item_box[i]
        cx_global = self.map_x * 13 + self.chara_x // 5
        cy_global = self.map_y * 13 + self.chara_y // 5
        self.obj_data[72][118] = cx_global
        self.obj_data[73][118] = cy_global

    def from_save_data(self, data):
        for y in range(78):
            for x in range(130):
                self.map_data[y][x] = data[y][0][x]
                self.obj_data[y][x] = data[y][1][x]
        self._restore_hidden_state()

    def _restore_hidden_state(self):
        self.hp = self.obj_data[66][118]
        self.attack = self.obj_data[67][118]
        self.defense = self.obj_data[68][118]
        self.gold = self.obj_data[69][118]
        self.altar_count = self.obj_data[66][119]
        self.highest_floor = self.obj_data[71][118]
        self.yellow_keys = self.obj_data[74][118]
        self.blue_keys = self.obj_data[75][118]
        self.red_keys = self.obj_data[76][118]
        self.weapon = self.obj_data[71][119]
        self.shield = self.obj_data[72][119]
        self.sound_mode = self.obj_data[72][124]
        self.bgm_mode = self.obj_data[75][124]
        self.language = self.obj_data[76][121]
        self.event_counter = self.obj_data[74][126]
        self.event_3f = self.obj_data[73][126]
        self.attack_double = 2 if self.obj_data[66][120] else 1
        self.double_gold = bool(self.obj_data[67][120])

        for i in range(15):
            if i < 6:
                row = 71 + i
                col = 119
            else:
                row = 66 + (i - 6)
                col = 120
            self.item_box[i] = self.obj_data[row][col]

        cx_local = self.obj_data[72][118]
        cy_local = self.obj_data[73][118]
        self.map_x = cx_local // 13
        self.map_y = cy_local // 13
        self.chara_x = (cx_local % 13) * 5
        self.chara_y = (cy_local % 13) * 5

        if self.hp <= 0:
            self.game_over = True
