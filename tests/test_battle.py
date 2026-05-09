import pytest
from magic_tower.battle import calc_battle, execute_battle, preview_battle
from magic_tower.game import ATR_ENERGY, ATR_STRENGTH, ATR_DEFENCE, ATR_GOLD


class TestCalcBattle:
    """Test the calc_battle function."""

    def test_cannot_break_defense(self, game_state, monster_attrs):
        """Test when player attack is too low to damage monster."""
        game_state.attack = 10
        game_state.defense = 10
        game_state.attack_double = 1
        obj_attr = monster_attrs["high_def_monster"]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is None

    def test_monster_zero_damage_to_player(self, game_state, monster_attrs):
        """Test when monster attack is lower than player defense."""
        game_state.attack = 100
        game_state.defense = 50
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 30, 20, 50, 0, 0, 0, 0, 0, 0]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        assert result["player_damage"] == 0
        assert result["can_win"] is True

    def test_normal_battle_calculation(self, game_state, monster_attrs):
        """Test normal battle damage calculation."""
        game_state.attack = 50
        game_state.defense = 10
        game_state.hp = 500
        game_state.attack_double = 1
        obj_attr = monster_attrs["weak_monster"]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        assert result["mon_hp"] == 50
        assert result["mon_atk"] == 10
        assert result["mon_def"] == 5
        assert result["mon_gold"] == 10
        assert result["damage_to_mon"] == 45
        assert result["rounds"] == 2
        assert result["player_damage"] == 0

    def test_attack_double_multiplier(self, game_state, monster_attrs):
        """Test attack_double multiplier effect."""
        game_state.attack = 50
        game_state.defense = 10
        game_state.attack_double = 2
        obj_attr = monster_attrs["weak_monster"]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        expected_damage = (50 * 2) - 5
        assert result["damage_to_mon"] == expected_damage

    def test_one_round_battle(self, game_state):
        """Test battle that finishes in one round."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 50, 10, 5, 10, 0, 0, 0, 0, 0, 0]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        assert result["rounds"] == 1
        assert result["player_damage"] == 0

    def test_can_win_determination(self, game_state):
        """Test can_win flag based on player HP vs damage."""
        game_state.attack = 50
        game_state.defense = 0
        game_state.hp = 100
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 50, 0, 20, 0, 0, 0, 0, 0, 0]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        assert "can_win" in result

    def test_battle_with_equal_defense(self, game_state):
        """Test when player attack equals monster defense."""
        game_state.attack = 50
        game_state.defense = 10
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 20, 50, 10, 0, 0, 0, 0, 0, 0]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is None

    def test_high_hp_monster_rounds(self, game_state):
        """Test rounds calculation for high HP monster."""
        game_state.attack = 50
        game_state.defense = 10
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 1000, 30, 10, 100, 0, 0, 0, 0, 0, 0]
        
        result = calc_battle(game_state, None, obj_attr)
        assert result is not None
        damage_per_round = 50 - 10
        expected_rounds = (1000 + damage_per_round - 1) // damage_per_round
        assert result["rounds"] == expected_rounds


class TestExecuteBattle:
    """Test the execute_battle function."""

    def test_execute_winning_battle(self, game_state, monkeypatch):
        """Test executing a battle that player can win."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.hp = 500
        game_state.attack_double = 1
        game_state.double_gold = False
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 20, 5, 50, 0, 0, 0, 0, 0, 0]
        
        result = execute_battle(game_state, None, obj_attr, 10, 10)
        assert result is not None
        assert game_state.gold == 50

    def test_execute_with_double_gold(self, game_state):
        """Test execute_battle with double_gold enabled."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.hp = 500
        game_state.attack_double = 1
        game_state.double_gold = True
        game_state.gold = 0
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 20, 5, 50, 0, 0, 0, 0, 0, 0]
        
        execute_battle(game_state, None, obj_attr, 10, 10)
        assert game_state.gold == 100

    def test_execute_battle_removes_monster(self, game_state):
        """Test that monster is removed from map after battle."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.hp = 500
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 20, 5, 50, 0, 0, 0, 0, 0, 0]
        game_state.set_object(10, 10, 5)
        
        execute_battle(game_state, None, obj_attr, 10, 10)
        assert game_state.get_object(10, 10) == 0

    def test_execute_battle_with_replacement_item(self, game_state):
        """Test execute_battle with monster that has replacement item."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.hp = 500
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 20, 5, 50, 1, 0, 0, 0, 0, 0]
        
        execute_battle(game_state, None, obj_attr, 10, 10)
        assert game_state.get_object(10, 10) == 1

    def test_execute_losing_battle(self, game_state):
        """Test executing a battle that causes game over."""
        game_state.attack = 50
        game_state.defense = 0
        game_state.hp = 100
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 500, 200, 0, 50, 0, 0, 0, 0, 0, 0]
        
        result = execute_battle(game_state, None, obj_attr, 10, 10)
        assert result is not None
        assert game_state.hp == 0
        assert game_state.game_over is True

    def test_execute_battle_cannot_attack(self, game_state):
        """Test execute_battle when player cannot attack."""
        game_state.attack = 10
        game_state.defense = 10
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 50, 100, 10, 0, 0, 0, 0, 0, 0]
        
        result = execute_battle(game_state, None, obj_attr, 10, 10)
        assert result is None

    def test_execute_battle_hp_reduced(self, game_state):
        """Test that player HP is correctly reduced after battle."""
        game_state.attack = 100
        game_state.defense = 10
        game_state.hp = 200
        game_state.attack_double = 1
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 30, 5, 50, 0, 0, 0, 0, 0, 0]
        
        initial_hp = game_state.hp
        execute_battle(game_state, None, obj_attr, 10, 10)
        assert game_state.hp < initial_hp


class TestPreviewBattle:
    """Test the preview_battle function."""

    def test_preview_cannot_attack(self, game_state):
        """Test preview when player cannot attack."""
        game_state.attack = 10
        game_state.defense = 10
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 50, 100, 10, 0, 0, 0, 0, 0, 0]
        
        result = preview_battle(game_state, obj_attr)
        assert result is not None
        assert result["can_attack"] is False
        assert result["player_damage"] == -1

    def test_preview_can_attack(self, game_state):
        """Test preview when player can attack."""
        game_state.attack = 100
        game_state.defense = 10
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 30, 5, 50, 0, 0, 0, 0, 0, 0]
        
        result = preview_battle(game_state, obj_attr)
        assert result is not None
        assert result["can_attack"] is True
        assert "player_damage" in result
        assert "rounds" in result

    def test_preview_no_damage_to_player(self, game_state):
        """Test preview when player defense >= monster attack."""
        game_state.attack = 100
        game_state.defense = 50
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 30, 10, 50, 0, 0, 0, 0, 0, 0]
        
        result = preview_battle(game_state, obj_attr)
        assert result is not None
        assert result["can_attack"] is True
        assert result["player_damage"] == 0

    def test_preview_rounds_calculation(self, game_state):
        """Test preview calculates correct rounds."""
        game_state.attack = 50
        game_state.defense = 10
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 200, 20, 5, 50, 0, 0, 0, 0, 0, 0]
        
        result = preview_battle(game_state, obj_attr)
        assert result is not None
        damage_per_round = 50 - 5
        expected_rounds = (200 + damage_per_round - 1) // damage_per_round
        assert result["rounds"] == expected_rounds

    def test_preview_monster_stats(self, game_state):
        """Test preview returns correct monster stats."""
        game_state.attack = 100
        game_state.defense = 10
        obj_attr = [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 150, 40, 15, 75, 0, 0, 0, 0, 0, 0]
        
        result = preview_battle(game_state, obj_attr)
        assert result is not None
        assert result["mon_hp"] == 150
        assert result["mon_atk"] == 40
        assert result["mon_def"] == 15
