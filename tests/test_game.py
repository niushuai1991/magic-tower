import pytest
from magic_tower.game import GameState, MAP_STREET, MAP_WALL, MAP_LOCALGATE, OBJ_NORMAL, OBJ_MESSAGE, OBJ_EQUIP, OBJ_ITEM, OBJ_DOOR, OBJ_MONSTER, OBJ_ALTAR, OBJ_KEY, OBJ_SCORE, OBJ_SELL, OBJ_BUY


class TestGameState:
    """Test GameState initialization and basic properties."""

    def test_initialization(self):
        """Test GameState initializes with default values."""
        game = GameState()
        assert game.hp == 1000
        assert game.attack == 100
        assert game.defense == 100
        assert game.gold == 0
        assert game.yellow_keys == 0
        assert game.blue_keys == 0
        assert game.red_keys == 0
        assert game.weapon == 0
        assert game.shield == 0
        assert game.highest_floor == 1
        assert game.attack_double == 1
        assert game.double_gold is False
        assert game.game_over is False
        assert game.game_won is False

    def test_map_data_dimensions(self):
        """Test map_data has correct dimensions."""
        game = GameState()
        assert len(game.map_data) == 78
        assert len(game.map_data[0]) == 130
        assert len(game.obj_data) == 78
        assert len(game.obj_data[0]) == 130

    def test_item_box_initialization(self):
        """Test item_box has 15 slots."""
        game = GameState()
        assert len(game.item_box) == 15
        assert all(item == 0 for item in game.item_box)

    def test_player_initial_position(self):
        """Test player starts at default position."""
        game = GameState()
        assert game.chara_x == 30
        assert game.chara_y == 55
        assert game.map_x == 0
        assert game.map_y == 0
        assert game.direction == 8

    def test_language_initialization(self):
        """Test language is initialized to English (0)."""
        game = GameState()
        assert game.language == 0

    def test_sound_mode_initialization(self):
        """Test sound mode is initialized."""
        game = GameState()
        assert game.sound_mode == 2
        assert game.bgm_mode == 0


class TestCoordinateConversion:
    """Test coordinate conversion methods."""

    def test_get_local_pos(self):
        """Test converting to local coordinates."""
        game = GameState()
        game.chara_x = 50
        game.chara_y = 55
        
        lx, ly = game.get_local_pos()
        assert lx == 10
        assert ly == 11

    def test_get_global_pos(self):
        """Test converting to global coordinates."""
        game = GameState()
        game.chara_x = 50
        game.chara_y = 55
        game.map_x = 1
        game.map_y = 2
        
        gx, gy = game.get_global_pos()
        assert gx == 1 * 13 + 10
        assert gy == 2 * 13 + 11

    def test_global_local_roundtrip(self):
        """Test global and local coordinate conversion is reversible."""
        game = GameState()
        game.chara_x = 45
        game.chara_y = 60
        game.map_x = 3
        game.map_y = 4
        
        gx, gy = game.get_global_pos()
        lx, ly = game.get_local_pos()
        
        assert gx == game.map_x * 13 + lx
        assert gy == game.map_y * 13 + ly


class TestCurrentFloor:
    """Test current_floor method."""

    def test_current_floor_floor_1(self):
        """Test current floor 1."""
        game = GameState()
        game.map_x = 0
        game.map_y = 0
        
        assert game.current_floor() == 1

    def test_current_floor_floor_10(self):
        """Test current floor 10."""
        game = GameState()
        game.map_x = 9
        game.map_y = 0
        
        assert game.current_floor() == 10

    def test_current_floor_floor_11(self):
        """Test current floor 11."""
        game = GameState()
        game.map_x = 0
        game.map_y = 1
        
        assert game.current_floor() == 11

    def test_current_floor_floor_50(self):
        """Test current floor 50."""
        game = GameState()
        game.map_x = 9
        game.map_y = 4
        
        assert game.current_floor() == 50


class TestMapOperations:
    """Test map and object operations."""

    def test_get_map_tile_valid(self):
        """Test getting valid map tile."""
        game = GameState()
        game.set_map_tile(10, 10, 5)
        
        assert game.get_map_tile(10, 10) == 5

    def test_get_map_tile_out_of_bounds(self):
        """Test getting map tile out of bounds returns wall."""
        game = GameState()
        
        assert game.get_map_tile(-1, 10) == MAP_WALL
        assert game.get_map_tile(130, 10) == MAP_WALL
        assert game.get_map_tile(10, -1) == MAP_WALL
        assert game.get_map_tile(10, 78) == MAP_WALL

    def test_set_map_tile_valid(self):
        """Test setting valid map tile."""
        game = GameState()
        game.set_map_tile(20, 20, 3)
        
        assert game.map_data[20][20] == 3

    def test_set_map_tile_out_of_bounds_ignored(self):
        """Test setting map tile out of bounds is ignored."""
        game = GameState()
        game.set_map_tile(-1, 10, 5)
        game.set_map_tile(130, 10, 5)
        game.set_map_tile(10, -1, 5)
        game.set_map_tile(10, 78, 5)
        
        assert game.map_data[10][10] == 0

    def test_get_object_valid(self):
        """Test getting valid object."""
        game = GameState()
        game.set_object(15, 15, 10)
        
        assert game.get_object(15, 15) == 10

    def test_get_object_out_of_bounds(self):
        """Test getting object out of bounds returns 0."""
        game = GameState()
        
        assert game.get_object(-1, 10) == 0
        assert game.get_object(130, 10) == 0
        assert game.get_object(10, -1) == 0
        assert game.get_object(10, 78) == 0

    def test_set_object_valid(self):
        """Test setting valid object."""
        game = GameState()
        game.set_object(25, 25, 7)
        
        assert game.obj_data[25][25] == 7

    def test_set_object_out_of_bounds_ignored(self):
        """Test setting object out of bounds is ignored."""
        game = GameState()
        game.set_object(-1, 10, 5)
        game.set_object(130, 10, 5)
        game.set_object(10, -1, 5)
        game.set_object(10, 78, 5)
        
        assert game.obj_data[10][10] == 0


class TestTotalAttack:
    """Test get_total_attack method."""

    def test_total_attack_no_weapon(self):
        """Test total attack with no weapon."""
        game = GameState()
        game.attack = 50
        game.weapon = 0
        
        assert game.get_total_attack() == 50

    def test_total_attack_with_weapon(self):
        """Test total attack with weapon."""
        game = GameState()
        game.attack = 50
        game.weapon = 30
        
        total = game.get_total_attack()
        assert total >= 50

    def test_total_attack_different_weapons(self):
        """Test total attack with different weapons."""
        game = GameState()
        game.attack = 30
        
        for weapon_id in [30, 31, 32, 33, 34, 35]:
            game.weapon = weapon_id
            total = game.get_total_attack()
            assert total >= 30


class TestTotalDefense:
    """Test get_total_defense method."""

    def test_total_defense_no_shield(self):
        """Test total defense with no shield."""
        game = GameState()
        game.defense = 30
        game.shield = 0
        
        assert game.get_total_defense() == 30

    def test_total_defense_with_shield(self):
        """Test total defense with shield."""
        game = GameState()
        game.defense = 30
        game.shield = 66
        
        total = game.get_total_defense()
        assert total >= 30

    def test_total_defense_different_shields(self):
        """Test total defense with different shields."""
        game = GameState()
        game.defense = 20
        
        for shield_id in [66, 67, 68, 76, 77, 78]:
            game.shield = shield_id
            total = game.get_total_defense()
            assert total >= 20


class TestLoadInitialMaps:
    """Test load_initial_maps method."""

    def test_load_initial_maps_creates_structure(self):
        """Test load_initial_maps creates map structure."""
        game = GameState()
        game.load_initial_maps()
        
        assert len(game.map_data) == 78
        assert len(game.map_data[0]) == 130

    def test_load_initial_maps_borders(self):
        """Test load_initial_maps creates borders."""
        game = GameState()
        game.load_initial_maps()
        
        assert game.map_data[0][0] == 30
        assert game.map_data[0][12] == 32
        assert game.map_data[12][0] == 35
        assert game.map_data[12][12] == 37


class TestToSaveData:
    """Test to_save_data method."""

    def test_to_save_data_structure(self):
        """Test to_save_data returns correct structure."""
        game = GameState()
        game.load_initial_maps()
        
        data = game.to_save_data()
        assert len(data) == 78
        assert len(data[0]) == 2
        assert len(data[0][0]) == 130
        assert len(data[0][1]) == 130

    def test_to_save_data_preserves_values(self):
        """Test to_save_data preserves map values."""
        game = GameState()
        game.load_initial_maps()
        game.set_map_tile(10, 10, 5)
        game.set_object(10, 10, 7)
        
        data = game.to_save_data()
        assert data[10][0][10] == 5
        assert data[10][1][10] == 7


class TestFromSaveData:
    """Test from_save_data method."""

    def test_from_save_data_restores_values(self):
        """Test from_save_data restores values."""
        game = GameState()
        game.load_initial_maps()
        data = game.to_save_data()
        
        game2 = GameState()
        game2.from_save_data(data)
        
        assert game2.map_data[10][10] == game.map_data[10][10]
        assert game2.obj_data[10][10] == game.obj_data[10][10]


class TestSetHiddenState:
    """Test _set_hidden_state method."""

    def test_set_hidden_state_stores_hp(self):
        """Test _set_hidden_state stores HP."""
        game = GameState()
        game.hp = 500
        game._set_hidden_state()
        
        assert game.obj_data[66][118] == 500

    def test_set_hidden_state_stores_attack(self):
        """Test _set_hidden_state stores attack."""
        game = GameState()
        game.attack = 150
        game._set_hidden_state()
        
        assert game.obj_data[67][118] == 150

    def test_set_hidden_state_stores_defense(self):
        """Test _set_hidden_state stores defense."""
        game = GameState()
        game.defense = 120
        game._set_hidden_state()
        
        assert game.obj_data[68][118] == 120

    def test_set_hidden_state_stores_gold(self):
        """Test _set_hidden_state stores gold."""
        game = GameState()
        game.gold = 999
        game._set_hidden_state()
        
        assert game.obj_data[69][118] == 999


class TestRestoreHiddenState:
    """Test _restore_hidden_state method."""

    def test_restore_hidden_state_restores_hp(self):
        """Test _restore_hidden_state restores HP."""
        game = GameState()
        game.obj_data[66][118] = 750
        game._restore_hidden_state()
        
        assert game.hp == 750

    def test_restore_hidden_state_restores_attack(self):
        """Test _restore_hidden_state restores attack."""
        game = GameState()
        game.obj_data[67][118] = 200
        game._restore_hidden_state()
        
        assert game.attack == 200

    def test_restore_hidden_state_restores_defense(self):
        """Test _restore_hidden_state restores defense."""
        game = GameState()
        game.obj_data[68][118] = 180
        game._restore_hidden_state()
        
        assert game.defense == 180

    def test_restore_hidden_state_restores_gold(self):
        """Test _restore_hidden_state restores gold."""
        game = GameState()
        game.obj_data[69][118] = 888
        game._restore_hidden_state()
        
        assert game.gold == 888

    def test_restore_hidden_state_restores_keys(self):
        """Test _restore_hidden_state restores keys."""
        game = GameState()
        game.obj_data[74][118] = 5
        game.obj_data[75][118] = 3
        game.obj_data[76][118] = 2
        game._restore_hidden_state()
        
        assert game.yellow_keys == 5
        assert game.blue_keys == 3
        assert game.red_keys == 2

    def test_restore_hidden_state_restores_equipment(self):
        """Test _restore_hidden_state restores equipment."""
        game = GameState()
        game.obj_data[71][119] = 30
        game.obj_data[72][119] = 66
        game._restore_hidden_state()
        
        assert game.weapon == 30
        assert game.shield == 66

    def test_restore_hidden_state_restores_position(self):
        """Test _restore_hidden_state restores position."""
        game = GameState()
        game.obj_data[72][118] = 50
        game.obj_data[73][118] = 65
        game._restore_hidden_state()
        
        assert game.map_x == 3
        assert game.map_y == 5
        assert game.chara_x == (50 % 13) * 5
        assert game.chara_y == (65 % 13) * 5

    def test_restore_hidden_state_sets_game_over(self):
        """Test _restore_hidden_state sets game_over when HP <= 0."""
        game = GameState()
        game.obj_data[66][118] = 0
        game._restore_hidden_state()
        
        assert game.game_over is True

    def test_restore_hidden_state_restores_attack_double(self):
        """Test _restore_hidden_state restores attack_double."""
        game = GameState()
        game.obj_data[66][120] = 1
        game._restore_hidden_state()
        
        assert game.attack_double == 2

    def test_restore_hidden_state_restores_double_gold(self):
        """Test _restore_hidden_state restores double_gold."""
        game = GameState()
        game.obj_data[67][120] = 1
        game._restore_hidden_state()
        
        assert game.double_gold is True

    def test_restore_hidden_state_with_zero_flags(self):
        """Test _restore_hidden_state with zero flags."""
        game = GameState()
        game.obj_data[66][120] = 0
        game.obj_data[67][120] = 0
        game._restore_hidden_state()
        
        assert game.attack_double == 1
        assert game.double_gold is False
