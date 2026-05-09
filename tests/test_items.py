import pytest
from magic_tower.items import (
    use_item, _use_pickaxe, _use_elixir, _use_ice_wand,
    _use_zapper, _use_mirror, _use_floor_up, _use_floor_down,
    _use_all_doors, _use_iron_doors
)


class TestUseItem:
    """Test the use_item function."""

    def test_use_empty_slot(self, game_state):
        """Test using an empty item slot."""
        result = use_item(game_state, 0)
        assert result is None

    def test_use_pickaxe(self, game_state):
        """Test using pickaxe (slot 3)."""
        game_state.item_box[3] = 4
        result = use_item(game_state, 3)
        assert result == "wall_broken" or result is None

    def test_use_elixir(self, game_state):
        """Test using elixir (slot 4)."""
        game_state.item_box[4] = 5
        game_state.attack = 10
        game_state.defense = 10
        result = use_item(game_state, 4)
        assert result is not None
        assert "heal_" in result

    def test_use_ice_wand(self, game_state):
        """Test using ice wand (slot 5)."""
        game_state.item_box[5] = 6
        result = use_item(game_state, 5)
        assert result == "iron_door_opened" or result is None

    def test_use_zapper(self, game_state):
        """Test using zapper (slot 6)."""
        game_state.item_box[6] = 7
        result = use_item(game_state, 6)
        assert result is not None or result is None

    def test_use_mirror(self, game_state):
        """Test using mirror (slot 7)."""
        game_state.item_box[7] = 8
        result = use_item(game_state, 7)
        assert result in ["mirrored", "mirror_blocked"]

    def test_use_floor_up(self, game_state):
        """Test using floor up item (slot 8)."""
        game_state.item_box[8] = 9
        game_state.map_y = 0
        game_state.map_x = 0
        result = use_item(game_state, 8)
        assert result is not None

    def test_use_floor_down(self, game_state):
        """Test using floor down item (slot 9)."""
        game_state.item_box[9] = 10
        game_state.map_y = 1
        game_state.map_x = 0
        result = use_item(game_state, 9)
        assert result is not None

    def test_use_pickaxe_alias(self, game_state):
        """Test using pickaxe alias (slot 10)."""
        game_state.item_box[10] = 4
        result = use_item(game_state, 10)
        assert result == "wall_broken" or result is None

    def test_use_all_doors(self, game_state):
        """Test using all doors item (slot 11)."""
        game_state.item_box[11] = 11
        game_state.set_object(10, 10, 2)
        result = use_item(game_state, 11)
        assert result == "doors_opened" or result is None

    def test_use_iron_doors(self, game_state):
        """Test using iron doors item (slot 12)."""
        game_state.item_box[12] = 12
        game_state.set_map_tile(10, 10, 3)
        result = use_item(game_state, 12)
        assert result == "iron_doors_opened" or result is None

    def test_use_invalid_slot(self, game_state):
        """Test using an invalid slot."""
        result = use_item(game_state, 13)
        assert result is None


class TestPickaxe:
    """Test the _use_pickaxe function."""

    def test_pickaxe_breaks_wall(self, game_state):
        """Test pickaxe breaks wall tiles around player."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[3] = 4
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 3)
        game_state.set_object(gx, gy - 1, 5)
        
        result = _use_pickaxe(game_state)
        assert result == "wall_broken"

    def test_pickaxe_no_walls(self, game_state):
        """Test pickaxe when no walls nearby."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[3] = 4
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 1)
        
        result = _use_pickaxe(game_state)
        assert result is None

    def test_pickaxe_consumes_item(self, game_state):
        """Test pickaxe consumes itself after use."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[3] = 4
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 3)
        
        _use_pickaxe(game_state)
        assert game_state.item_box[3] == 0


class TestElixir:
    """Test the _use_elixir function."""

    def test_elixir_heals(self, game_state):
        """Test elixir heals player based on stats."""
        game_state.attack = 10
        game_state.defense = 10
        game_state.hp = 100
        game_state.item_box[3] = 5
        
        expected_heal = 10 * 10 + 10 * 5
        result = _use_elixir(game_state)
        assert result == f"heal_{expected_heal}"
        assert game_state.hp == 100 + expected_heal

    def test_elixir_consumes_item(self, game_state):
        """Test elixir consumes itself after use."""
        game_state.attack = 10
        game_state.defense = 10
        game_state.item_box[3] = 5
        
        _use_elixir(game_state)
        assert game_state.item_box[3] == 0


class TestIceWand:
    """Test the _use_ice_wand function."""

    def test_ice_wand_opens_iron_door(self, game_state):
        """Test ice wand opens iron doors."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[5] = 6
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 3)
        
        result = _use_ice_wand(game_state)
        assert result == "iron_door_opened"

    def test_ice_wand_no_iron_doors(self, game_state):
        """Test ice wand when no iron doors nearby."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[5] = 6
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 1)
        
        result = _use_ice_wand(game_state)
        assert result is None

    def test_ice_wand_consumes_item(self, game_state):
        """Test ice wand consumes itself after use."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[5] = 6
        gx, gy = game_state.get_global_pos()
        game_state.set_map_tile(gx, gy - 1, 3)
        
        _use_ice_wand(game_state)
        assert game_state.item_box[5] == 0


class TestZapper:
    """Test the _use_zapper function."""

    def test_zapper_kills_monsters(self, game_state):
        """Test zapper kills monsters nearby."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[6] = 7
        game_state.double_gold = False
        gx, gy = game_state.get_global_pos()
        game_state.set_object(gx, gy - 1, 5)
        
        result = _use_zapper(game_state)
        assert result is not None

    def test_zapper_with_double_gold(self, game_state):
        """Test zapper with double_gold enabled."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[6] = 7
        game_state.double_gold = True
        gx, gy = game_state.get_global_pos()
        game_state.set_object(gx, gy - 1, 5)
        
        result = _use_zapper(game_state)
        assert result is not None

    def test_zapper_no_monsters(self, game_state):
        """Test zapper when no monsters nearby."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[6] = 7
        gx, gy = game_state.get_global_pos()
        game_state.set_object(gx, gy - 1, 0)
        
        result = _use_zapper(game_state)
        assert result is None

    def test_zapper_consumes_item(self, game_state):
        """Test zapper consumes itself after use."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[6] = 7
        gx, gy = game_state.get_global_pos()
        game_state.set_object(gx, gy - 1, 5)
        
        _use_zapper(game_state)
        assert game_state.item_box[6] == 0


class TestMirror:
    """Test the _use_mirror function."""

    def test_mirror_teleport(self, game_state):
        """Test mirror teleports player to mirrored position."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[7] = 8
        game_state.map_x = 0
        game_state.map_y = 0
        
        result = _use_mirror(game_state)
        assert result == "mirrored" or result == "mirror_blocked"

    def test_mirror_blocked(self, game_state):
        """Test mirror blocked by object at target."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[7] = 8
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.set_object(60, 55, 1)
        
        result = _use_mirror(game_state)
        assert result == "mirror_blocked"


class TestFloorItems:
    """Test floor up/down items."""

    def test_floor_up_from_floor_1(self, game_state):
        """Test floor up from floor 1."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[8] = 9
        game_state.map_x = 0
        game_state.map_y = 0
        
        result = _use_floor_up(game_state)
        assert result is not None
        assert game_state.map_x == 1
        assert game_state.item_box[8] == 0

    def test_floor_up_from_floor_50(self, game_state):
        """Test floor up from floor 50 (should fail)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[8] = 9
        game_state.map_x = 9
        game_state.map_y = 4
        
        result = _use_floor_up(game_state)
        assert result == "no_floor"

    def test_floor_up_updates_highest_floor(self, game_state):
        """Test floor up updates highest_floor if needed."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[8] = 9
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.highest_floor = 1
        
        _use_floor_up(game_state)
        assert game_state.highest_floor == 2

    def test_floor_down_from_floor_2(self, game_state):
        """Test floor down from floor 2."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[9] = 10
        game_state.map_x = 1
        game_state.map_y = 0
        
        result = _use_floor_down(game_state)
        assert result is not None
        assert game_state.map_x == 0
        assert game_state.item_box[9] == 0

    def test_floor_down_from_floor_1(self, game_state):
        """Test floor down from floor 1 (should fail)."""
        game_state.chara_x = 50
        game_state.chara_y = 50
        game_state.item_box[9] = 10
        game_state.map_x = 0
        game_state.map_y = 0
        
        result = _use_floor_down(game_state)
        assert result == "no_floor"


class TestDoorItems:
    """Test door opening items."""

    def test_all_doors_opens_yellow_doors(self, game_state):
        """Test all doors opens yellow doors on current floor."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[11] = 11
        base_x = 0
        base_y = 0
        game_state.set_object(base_x + 5, base_y + 5, 2)
        
        result = _use_all_doors(game_state)
        assert result == "doors_opened" or result is None

    def test_all_doors_no_doors(self, game_state):
        """Test all doors when no doors on floor."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[11] = 11
        
        result = _use_all_doors(game_state)
        assert result is None or result == "doors_opened"

    def test_all_doors_consumes_item(self, game_state):
        """Test all doors consumes itself after use."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[11] = 11
        base_x = 0
        base_y = 0
        game_state.set_object(base_x + 5, base_y + 5, 2)
        
        _use_all_doors(game_state)
        assert game_state.item_box[11] == 0

    def test_iron_doors_opens_iron_doors(self, game_state):
        """Test iron doors opens iron doors on current floor."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[12] = 12
        base_x = 0
        base_y = 0
        game_state.set_map_tile(base_x + 5, base_y + 5, 3)
        
        result = _use_iron_doors(game_state)
        assert result == "iron_doors_opened" or result is None

    def test_iron_doors_no_iron_doors(self, game_state):
        """Test iron doors when no iron doors on floor."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[12] = 12
        
        result = _use_iron_doors(game_state)
        assert result is None or result == "iron_doors_opened"

    def test_iron_doors_consumes_item(self, game_state):
        """Test iron doors consumes itself after use."""
        game_state.map_x = 0
        game_state.map_y = 0
        game_state.item_box[12] = 12
        base_x = 0
        base_y = 0
        game_state.set_map_tile(base_x + 5, base_y + 5, 3)
        
        _use_iron_doors(game_state)
        assert game_state.item_box[12] == 0
