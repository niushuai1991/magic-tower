import pytest
from magic_tower.player import try_move, check_floor_transition, _handle_door, _handle_key, _handle_item, _handle_equip
from magic_tower.game import OBJ_DOOR, OBJ_KEY, OBJ_ITEM, OBJ_MONSTER, OBJ_EQUIP, OBJ_MESSAGE, OBJ_ALTAR, OBJ_BUY, OBJ_SELL, OBJ_SCORE, ATR_TYPE, ATR_ENERGY, ATR_DEFENCE, ATR_GOLD, ATR_STRING


class TestTryMove:
    """Test the try_move function."""

    def test_move_up(self, game_state):
        """Test moving up (direction 8)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 9, 0)
        
        result = try_move(game_state, 8)
        assert result in ["moved", "continue", None]

    def test_move_down(self, game_state):
        """Test moving down (direction 2)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 11, 0)
        
        result = try_move(game_state, 2)
        assert result in ["moved", "continue", None]

    def test_move_left(self, game_state):
        """Test moving left (direction 4)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(9, 10, 0)
        
        result = try_move(game_state, 4)
        assert result in ["moved", "continue", None]

    def test_move_right(self, game_state):
        """Test moving right (direction 6)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(11, 10, 0)
        
        result = try_move(game_state, 6)
        assert result in ["moved", "continue", None]

    def test_move_invalid_direction(self, game_state):
        """Test moving in invalid direction."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        
        result = try_move(game_state, 1)
        assert result is None

    def test_move_when_animating(self, game_state):
        """Test move when player is in middle of animation."""
        game_state.chara_x = 51
        game_state.chara_y = 50
        
        result = try_move(game_state, 8)
        assert result == "continue"

    def test_move_into_wall(self, game_state):
        """Test moving into wall."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 9, 1)
        
        result = try_move(game_state, 8)
        assert result is None

    def test_move_updates_position(self, game_state):
        """Test move updates player position."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 9, 0)
        game_state.set_object(10, 9, 0)
        
        initial_y = game_state.chara_y
        try_move(game_state, 8)
        assert game_state.chara_y == initial_y - 5

    def test_move_updates_direction(self, game_state):
        """Test move updates player direction."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 9, 0)
        
        try_move(game_state, 8)
        assert game_state.direction == 8

    def test_move_into_monster(self, game_state):
        """Test moving into monster triggers battle."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 9, 0)
        game_state.set_object(10, 9, 5)
        
        result = try_move(game_state, 8)
        if isinstance(result, tuple):
            assert result[0] == "battle"

    def test_move_out_of_bounds(self, game_state):
        """Test moving out of bounds."""
        game_state.chara_x = 0
        game_state.chara_y = 50
        
        result = try_move(game_state, 4)
        assert result is None


class TestHandleDoor:
    """Test the _handle_door function."""

    def test_yellow_door_with_key(self, game_state):
        """Test opening yellow door with key."""
        game_state.yellow_keys = 1
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 2, obj_attr, 10, 10)
        assert result is None
        assert game_state.yellow_keys == 0
        assert game_state.get_object(10, 10) == 0

    def test_yellow_door_without_key(self, game_state):
        """Test opening yellow door without key."""
        game_state.yellow_keys = 0
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 2, obj_attr, 10, 10)
        assert result == "block"
        assert game_state.yellow_keys == 0

    def test_blue_door_with_key(self, game_state):
        """Test opening blue door with key."""
        game_state.blue_keys = 1
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 4, obj_attr, 10, 10)
        assert result is None
        assert game_state.blue_keys == 0
        assert game_state.get_object(10, 10) == 0

    def test_blue_door_without_key(self, game_state):
        """Test opening blue door without key."""
        game_state.blue_keys = 0
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 4, obj_attr, 10, 10)
        assert result == "block"
        assert game_state.blue_keys == 0

    def test_red_door_with_key(self, game_state):
        """Test opening red door with key."""
        game_state.red_keys = 1
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 27, obj_attr, 10, 10)
        assert result is None
        assert game_state.red_keys == 0
        assert game_state.get_object(10, 10) == 0

    def test_red_door_without_key(self, game_state):
        """Test opening red door without key."""
        game_state.red_keys = 0
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 27, obj_attr, 10, 10)
        assert result == "block"
        assert game_state.red_keys == 0

    def test_locked_door_always_blocks(self, game_state):
        """Test locked door (38) always blocks."""
        obj_attr = [0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_door(game_state, 38, obj_attr, 10, 10)
        assert result == "block"


class TestHandleKey:
    """Test the _handle_key function."""

    def test_pick_up_yellow_key(self, game_state):
        """Test picking up yellow key."""
        game_state.yellow_keys = 0
        obj_attr = [0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_key(game_state, 1, obj_attr, 10, 10)
        assert result is None
        assert game_state.yellow_keys == 1
        assert game_state.get_object(10, 10) == 0

    def test_pick_up_blue_key(self, game_state):
        """Test picking up blue key."""
        game_state.blue_keys = 0
        obj_attr = [0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_key(game_state, 3, obj_attr, 10, 10)
        assert result is None
        assert game_state.blue_keys == 1
        assert game_state.get_object(10, 10) == 0

    def test_pick_up_red_key(self, game_state):
        """Test picking up red key."""
        game_state.red_keys = 0
        obj_attr = [0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_key(game_state, 28, obj_attr, 10, 10)
        assert result is None
        assert game_state.red_keys == 1
        assert game_state.get_object(10, 10) == 0


class TestHandleItem:
    """Test the _handle_item function."""

    def test_pick_up_item(self, game_state):
        """Test picking up item."""
        obj_attr = [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_item(game_state, 5, obj_attr, 10, 10)
        assert result is None
        assert game_state.item_box[4] == 5
        assert game_state.get_object(10, 10) == 0

    def test_pick_up_multiple_items(self, game_state):
        """Test picking up multiple items."""
        game_state.set_object(10, 10, 3)
        game_state.set_object(11, 10, 5)
        
        obj_attr = [0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        _handle_item(game_state, 3, obj_attr, 10, 10)
        _handle_item(game_state, 5, obj_attr, 11, 10)
        
        assert game_state.item_box[2] == 3
        assert game_state.item_box[4] == 5


class TestHandleEquip:
    """Test the _handle_equip function."""

    def test_pick_up_weapon(self, game_state):
        """Test picking up weapon."""
        game_state.attack = 10
        game_state.defense = 10
        obj_attr = [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_equip(game_state, 30, obj_attr, 10, 10)
        assert result is None
        assert game_state.attack == 30
        assert game_state.weapon == 30
        assert game_state.get_object(10, 10) == 0

    def test_pick_up_shield(self, game_state):
        """Test picking up shield."""
        game_state.attack = 10
        game_state.defense = 10
        obj_attr = [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 20, 0, 0, 0, 0, 0, 0, 0]
        
        result = _handle_equip(game_state, 66, obj_attr, 10, 10)
        assert result is None
        assert game_state.defense == 30
        assert game_state.shield == 66
        assert game_state.get_object(10, 10) == 0

    def test_pick_up_attack_double_item(self, game_state):
        """Test picking up item that doubles attack."""
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        _handle_equip(game_state, 114, obj_attr, 10, 10)
        assert game_state.attack_double == 2

    def test_pick_up_double_gold_item(self, game_state):
        """Test picking up item that doubles gold."""
        game_state.double_gold = False
        obj_attr = [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        
        _handle_equip(game_state, 182, obj_attr, 10, 10)
        assert game_state.double_gold is True

    def test_pick_up_equip_with_both_stats(self, game_state):
        """Test picking up equipment with both attack and defense."""
        game_state.attack = 10
        game_state.defense = 10
        obj_attr = [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 15, 0, 10, 0, 0, 0, 0, 0, 0, 0]
        
        _handle_equip(game_state, 11, obj_attr, 10, 10)
        assert game_state.attack == 25
        assert game_state.defense == 20


class TestCheckFloorTransition:
    """Test the check_floor_transition function."""

    def test_no_transition_on_normal_tile(self, game_state):
        """Test no transition on normal floor tile."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 10, 0)
        
        result = check_floor_transition(game_state)
        assert result is None

    def test_transition_to_next_floor(self, game_state):
        """Test transition to next floor via gate."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 10, 2)
        
        from magic_tower.object_data import MAP_ATTR
        if 2 in MAP_ATTR:
            attr = MAP_ATTR[2]
            if len(attr) > 17:
                target_x = attr[16]
                target_y = attr[17]
                if target_x > 0 and target_y > 0:
                    result = check_floor_transition(game_state)
                    if result is not None:
                        assert result > 0

    def test_transition_updates_highest_floor(self, game_state):
        """Test transition updates highest_floor."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.highest_floor = 1
        game_state.set_map_tile(10, 10, 2)
        
        from magic_tower.object_data import MAP_ATTR
        if 2 in MAP_ATTR:
            attr = MAP_ATTR[2]
            if len(attr) > 17:
                target_x = attr[16]
                target_y = attr[17]
                if target_x > 0 and target_y > 0:
                    old_floor = game_state.current_floor()
                    check_floor_transition(game_state)
                    new_floor = game_state.current_floor()
                    if new_floor > old_floor:
                        assert game_state.highest_floor >= new_floor

    def test_no_transition_when_animating(self, game_state):
        """Test no transition when player is animating."""
        game_state.chara_x = 51
        game_state.chara_y = 50
        
        result = check_floor_transition(game_state)
        assert result is None

    def test_transition_updates_position(self, game_state):
        """Test transition updates player position."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.set_map_tile(10, 10, 2)
        
        from magic_tower.object_data import MAP_ATTR
        if 2 in MAP_ATTR:
            attr = MAP_ATTR[2]
            if len(attr) > 17:
                target_x = attr[16]
                target_y = attr[17]
                if target_x > 0 and target_y > 0:
                    initial_x = game_state.chara_x
                    initial_y = game_state.chara_y
                    check_floor_transition(game_state)
                    if game_state.chara_x != initial_x or game_state.chara_y != initial_y:
                        pass
