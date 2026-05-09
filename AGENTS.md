# Magic Tower Python - Agent Instructions

Python implementation of Magic Tower RPG game based on Japanese version 0.8a.

## Running the Game

```bash
# Install dependencies (uses uv)
uv sync

# Run the game
python -m magic_tower.main

# Or after installation:
magic-tower
```

## Architecture

**Entry Point**: `src/magic_tower/main.py` (NOT root `main.py`, which is a placeholder)

**Core Modules**:
- `game.py` - GameState class, map data structure (78x130 global grid), constants
- `player.py` - Movement, collision detection, interaction logic
- `battle.py` - Turn-based combat calculations
- `renderer.py` - Pygame rendering, UI panels
- `sprites.py` - Asset loading from `assets/` directory
- `save_load.py` - Binary save files in `savedat/` directory
- `items.py` - Item usage logic
- `events.py` - Floor-specific event triggers
- `audio.py` - Sound effects and BGM playback
- `interaction.py` - NPC, altar, shop interactions

## Auto-Generated Data

`src/magic_tower/map_data.py` and `src/magic_tower/object_data.py` are **auto-generated** from decompiled Java source using `convert_java_data.py`.

**To regenerate game data**:
```bash
python convert_java_data.py <input.java> src/magic_tower/
```

Do NOT manually edit these files - changes will be overwritten.

## Coordinate System

- Global map: 78 rows × 130 columns (fits 50 floors of 13×13 tiles each)
- Each floor: 13×13 tiles, 40px per tile
- Direction constants: `8=up, 2=down, 4=left, 6=right`
- Player position tracked in global coordinates, converted to floor-local for rendering

## Dependencies & Environment

- Python 3.12 (see `.python-version`)
- pygame-ce (Community Edition) >= 2.5.7 - **NOT** regular pygame
- Package manager: uv (see `uv.lock`)
- Build system: hatchling

## Key Constants (from `game.py`)

**Object Types**: `OBJ_NORMAL=0, OBJ_MESSAGE=1, OBJ_EQUIP=3, OBJ_ITEM=4, OBJ_DOOR=5, OBJ_MONSTER=6, OBJ_ALTAR=7, OBJ_KEY=8, OBJ_SCORE=11, OBJ_SELL=14, OBJ_BUY=15`

**Attribute Indices**: `ATR_TYPE=3, ATR_STRING=5, ATR_ENERGY=10, ATR_STRENGTH=11, ATR_DEFENCE=12, ATR_GOLD=13, ATR_ITEM=14`

**Tile Types**: `MAP_STREET=0, MAP_WALL=1, MAP_LOCALGATE=2`

## Save System

- Binary format stored in `savedat/data{slot}.dat` (slots 1-8)
- Saves: 78×130 object grid + 78×130 tile grid (big-endian uint16)
- Use `save_game(game, slot)` and `load_game(game, slot)` from `save_load.py`

## Multilingual Support

Game supports 3 languages (toggled with F12):
- Language 0: English
- Language 1: Japanese  
- Language 2: Chinese

Messages stored in `object_data.py::MESSAGES[lang][msg_id]`

## No Testing/CI

This project has no tests, linting, type checking, or CI configured. When making changes, manually verify:
1. Game launches without errors
2. Basic movement and interactions work
3. Save/load functionality works
4. Audio plays (if enabled)