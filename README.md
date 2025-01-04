# Adventure!

A procedurally generated roguelike game built with Python and Pygame.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run setup:
```bash
python setup.py install
```

## Building

Use `build.py` to create an executable:
```bash
python build.py
```

The executable will be created in the `dist` directory.

## Project Structure

```
├── build.py                     # Build script for creating executable
├── requirements.txt             # Project dependencies
├── setup.py                     # Package configuration
├── src/                         # Source code
    ├── combat/                  # Combat system
    │   ├── combat_manager.py    # Combat mechanics and encounters
    │   ├── entity.py            # Base classes for game entities
    ├── config/                  # Configuration files
    │   ├── biomes.json          # Biome definitions
    │   ├── font_config.py       # Font management
    │   ├── font_support.json    # Font character support
    │   ├── game_config.py       # Game settings
    │   ├── monsters.json        # Monster definitions
    ├── engine/                  # Core game systems
    │   ├── game_engine.py       # Main game loop and mechanics
    │   ├── menu.py              # Menu system
    │   ├── player.py            # Player character functionality
    ├── UI/                      # User interface components
    │   ├── combat_ui.py         # Combat interface
    │   ├── inventory_ui.py      # Inventory management UI
    ├── world/                   # World generation
    │   ├── terrain_generator.py # Procedural terrain generation
    │   ├── world.py             # World management
    │   ├── world_chunk.py       # Chunk-based world representation
```

## Key Components

### Combat System
- `combat_manager.py`: Combat mechanics and encounter generation
- `entity.py`: Entity system for players and monsters with stats, leveling, and combat logic

### World Generation
- `terrain_generator.py`: Procedural terrain generation using noise
- `world.py`: World management with chunked loading
- `world_chunk.py`: Individual world chunk data

### Game Engine
- `game_engine.py`: Core game loop, rendering, and state management
- `menu.py`: Menu system with save/load functionality
- `player.py`: Player character with movement and progression

### User Interface
- `combat_ui.py`: Turn-based combat interface with action selection
- `inventory_ui.py`: Equipment and inventory management system

### Configuration
- `biomes.json`: Biome definitions with characters, colors, and environmental parameters
- `monsters.json`: Monster definitions with stats and spawn rules
- `font_config.py`: Font management with character support verification
- `game_config.py`: Core game settings and constants

## Save System
Game saves are stored in:
- Windows: `%APPDATA%/Adventure/save.json`