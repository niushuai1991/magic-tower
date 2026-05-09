import pytest
from magic_tower.game import GameState, OBJ_MONSTER, OBJ_DOOR, OBJ_KEY, OBJ_ITEM, OBJ_EQUIP, OBJ_MESSAGE, OBJ_ALTAR, OBJ_BUY, OBJ_SELL, OBJ_SCORE


@pytest.fixture
def game_state():
    """Create a fresh GameState instance for testing."""
    game = GameState()
    game.load_initial_maps()
    return game


@pytest.fixture
def monster_attrs():
    """Provide test monster attributes."""
    return {
        "weak_monster": [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 50, 10, 5, 10, 0, 0, 0, 0, 0, 0],
        "strong_monster": [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 500, 100, 50, 500, 0, 0, 0, 0, 0, 0],
        "high_def_monster": [0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 100, 5, 200, 100, 0, 0, 0, 0, 0, 0],
    }


@pytest.fixture
def equip_attrs():
    """Provide test equipment attributes."""
    return {
        "weak_sword": [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "strong_sword": [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "weak_shield": [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 5, 0, 10, 0, 0, 0, 0, 0, 0, 0],
        "strong_shield": [0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 50, 0, 100, 0, 0, 0, 0, 0, 0, 0],
    }


@pytest.fixture
def game_with_player_stats(game_state):
    """Create a game with specific player stats for testing."""
    game = game_state
    game.hp = 1000
    game.attack = 100
    game.defense = 50
    game.gold = 100
    game.yellow_keys = 2
    game.blue_keys = 1
    game.red_keys = 0
    return game


@pytest.fixture
def game_with_equipment(game_state):
    """Create a game with equipment for testing attack/defense bonuses."""
    game = game_state
    game.attack = 50
    game.defense = 30
    game.weapon = 30
    game.shield = 66
    return game


@pytest.fixture
def game_at_position(game_state):
    """Create a game with player at specific position."""
    game = game_state
    game.chara_x = 50
    game.chara_y = 50
    game.map_x = 0
    game.map_y = 0
    return game


@pytest.fixture
def temp_save_dir(tmp_path):
    """Provide a temporary directory for save files."""
    return tmp_path / "savedat"
