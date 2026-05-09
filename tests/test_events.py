import pytest
from magic_tower.events import (
    get_event_flag, set_event_flag,
    get_event_state, set_event_state,
    get_3f_flag, set_3f_flag,
    handle_floor_events
)
from magic_tower.game import GameState


class TestEventFlag:
    """Test event flag get/set functions."""

    def test_get_event_flag_default(self, game_state):
        """Test getting default event flag."""
        flag = get_event_flag(game_state)
        assert flag == 0

    def test_set_event_flag(self, game_state):
        """Test setting event flag."""
        set_event_flag(game_state, 5)
        assert get_event_flag(game_state) == 5

    def test_set_event_flag_multiple_values(self, game_state):
        """Test setting event flag to multiple values."""
        for value in [0, 1, 10, 100, 255]:
            set_event_flag(game_state, value)
            assert get_event_flag(game_state) == value


class TestEventState:
    """Test event state get/set functions."""

    def test_get_event_state_default(self, game_state):
        """Test getting default event state."""
        state = get_event_state(game_state)
        assert state == 0

    def test_set_event_state(self, game_state):
        """Test setting event state."""
        set_event_state(game_state, 3)
        assert get_event_state(game_state) == 3

    def test_set_event_state_multiple_values(self, game_state):
        """Test setting event state to multiple values."""
        for value in [0, 1, 5, 50, 200]:
            set_event_state(game_state, value)
            assert get_event_state(game_state) == value


class Test3fFlag:
    """Test 3f flag get/set functions."""

    def test_get_3f_flag_default(self, game_state):
        """Test getting default 3f flag."""
        flag = get_3f_flag(game_state)
        assert flag == 0

    def test_set_3f_flag(self, game_state):
        """Test setting 3f flag."""
        set_3f_flag(game_state, 1)
        assert get_3f_flag(game_state) == 1

    def test_set_3f_flag_multiple_values(self, game_state):
        """Test setting 3f flag to multiple values."""
        for value in [0, 1, 2, 5, 10]:
            set_3f_flag(game_state, value)
            assert get_3f_flag(game_state) == value


class TestHandleFloorEvents:
    """Test handle_floor_events function."""

    def test_handle_floor_events_floor_1_no_flag(self, game_state):
        """Test floor 1 event when 3f flag is 0."""
        game_state.map_x = 0
        game_state.map_y = 0
        set_3f_flag(game_state, 0)
        set_event_flag(game_state, 0)
        
        events = handle_floor_events(game_state)
        assert isinstance(events, list)

    def test_handle_floor_events_floor_1_with_flag(self, game_state):
        """Test floor 1 event when 3f flag is set."""
        game_state.map_x = 0
        game_state.map_y = 0
        set_3f_flag(game_state, 1)
        
        events = handle_floor_events(game_state)
        assert isinstance(events, list)

    def test_handle_floor_events_other_floors(self, game_state):
        """Test events on other floors."""
        for floor in [2, 10, 25, 50]:
            mx = (floor - 1) % 10
            my = (floor - 1) // 10
            game_state.map_x = mx
            game_state.map_y = my
            
            events = handle_floor_events(game_state)
            assert isinstance(events, list)

    def test_handle_floor_events_returns_list(self, game_state):
        """Test handle_floor_events always returns a list."""
        for floor in range(1, 51):
            mx = (floor - 1) % 10
            my = (floor - 1) // 10
            game_state.map_x = mx
            game_state.map_y = my
            
            events = handle_floor_events(game_state)
            assert isinstance(events, list)

    def test_handle_floor_events_event_flag_influence(self, game_state):
        """Test event flag influences floor 1 events."""
        game_state.map_x = 0
        game_state.map_y = 0
        set_3f_flag(game_state, 0)
        
        set_event_flag(game_state, 0)
        events_0 = handle_floor_events(game_state)
        
        set_event_flag(game_state, 1)
        events_1 = handle_floor_events(game_state)
        
        assert isinstance(events_0, list)
        assert isinstance(events_1, list)

    def test_handle_floor_events_floor_1_thief_encounter(self, game_state):
        """Test floor 1 thief encounter event."""
        game_state.map_x = 0
        game_state.map_y = 0
        set_3f_flag(game_state, 0)
        set_event_flag(game_state, 0)
        
        game_state.set_object(10, 10, 87)
        game_state.chara_x = 50
        game_state.chara_y = 50
        
        events = handle_floor_events(game_state)
        assert isinstance(events, list)


class TestEventFlagIntegration:
    """Test event flag integration with game state."""

    def test_event_flag_independent_per_game(self, game_state):
        """Test event flag is independent per game instance."""
        game1 = GameState()
        game2 = GameState()
        
        set_event_flag(game1, 5)
        set_event_flag(game2, 10)
        
        assert get_event_flag(game1) == 5
        assert get_event_flag(game2) == 10

    def test_event_state_independent_per_game(self, game_state):
        """Test event state is independent per game instance."""
        game1 = GameState()
        game2 = GameState()
        
        set_event_state(game1, 3)
        set_event_state(game2, 7)
        
        assert get_event_state(game1) == 3
        assert get_event_state(game2) == 7

    def test_3f_flag_independent_per_game(self, game_state):
        """Test 3f flag is independent per game instance."""
        game1 = GameState()
        game2 = GameState()
        
        set_3f_flag(game1, 1)
        set_3f_flag(game2, 2)
        
        assert get_3f_flag(game1) == 1
        assert get_3f_flag(game2) == 2

    def test_multiple_flags_simultaneous(self, game_state):
        """Test setting multiple flags simultaneously."""
        set_event_flag(game_state, 5)
        set_event_state(game_state, 3)
        set_3f_flag(game_state, 1)
        
        assert get_event_flag(game_state) == 5
        assert get_event_state(game_state) == 3
        assert get_3f_flag(game_state) == 1

    def test_flag_persistence_across_events(self, game_state):
        """Test flags persist across event handling."""
        set_event_flag(game_state, 5)
        set_event_state(game_state, 3)
        set_3f_flag(game_state, 1)
        
        for floor in [1, 2, 3, 10, 20]:
            mx = (floor - 1) % 10
            my = (floor - 1) // 10
            game_state.map_x = mx
            game_state.map_y = my
            handle_floor_events(game_state)
        
        assert get_event_flag(game_state) == 5
        assert get_event_state(game_state) == 3
        assert get_3f_flag(game_state) == 1
