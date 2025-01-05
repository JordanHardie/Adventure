# Adventure!

A procedurally generated roguelike game built with Python and Pygame.

## Features
- Procedural world generation with diverse biomes
- Turn-based combat system with strategic elements
- Character progression and equipment system
- Dynamic monster encounters based on world location
- Customizable character development
- Save/Load functionality

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
├── combat/
│   ├── combat_manager.py    # Manages combat mechanics and turn processing
│   ├── encounter_manager.py    # Manages monster encounters and spawning based on world position and biome
│   ├── entity.py    # Defines entity types and their stats
│   ├── loot_generator.py    # Handles generation of items and gold drops from monsters
│   ├── name_generator.py    # Generates names for items using quality-based prefixes and descriptions
├── config/
│   ├── biomes.json    # Biome definitions and parameters
│   ├── descriptions.json    # Item description components
│   ├── font_config.py    # Font configuration and management
│   ├── font_support.json    # Font character support mapping
│   ├── game_config.py    # Core game settings and constants
│   ├── items.json    # Item definitions and properties
│   ├── monsters.json    # Monster definitions and spawn rules
│   ├── prefixes.json    # Quality-based item prefix definitions
├── engine/
│   ├── game_engine.py    # Core game engine managing game state, rendering, and user input
│   ├── player.py    # Player character functionality and inventory management
├── UI/
│   ├── combat_log_ui.py    # Displays combat and loot messages during gameplay
│   ├── combat_ui.py    # Combat interface management
│   ├── inventory_ui.py    # Inventory interface and equipment management
│   ├── level_up_ui.py    # Level up interface and stat allocation
│   ├── menu.py    # Menu system and game state management
├── world/
│   ├── terrain_generator.py    # Procedural terrain generation
│   ├── world.py    # World management and chunk loading
│   ├── world_chunk.py    # World chunk data structure
├── tools/
│   ├── readme_generator.py    # Automatic README.md generation
├── build.py    # Build script for executable creation
├── requirements.txt    # Project dependencies
├── setup.py    # Package configuration
```
```

## TODO

## Combat System
- combat_manager.py: Manages combat mechanics and turn processing
- encounter_manager.py: Manages monster encounters and spawning based on world position
- entity.py: Defines entity types and their stats
- loot_generator.py: Handles generation of items and gold drops from monsters
- name_generator.py: Generates names for items using quality-based prefixes and descriptions

## World Generation
- terrain_generator.py: Procedural terrain generation with noise maps
- world.py: World management with chunked loading and biome determination
- world_chunk.py: Chunk-based world data structure

## Game Engine
- game_engine.py: Core game engine managing game state, rendering, and user input
- player.py: Player character functionality and inventory management

## User Interface
- combat_log_ui.py: Displays combat and loot messages during gameplay
- combat_ui.py: Combat interface and turn management
- inventory_ui.py: Inventory and equipment management interface
- level_up_ui.py: Character progression and stat allocation
- menu.py: Menu system with save/load functionality

## Configuration
- font_config.py: Font configuration and management
- game_config.py: Core game settings and constants
- items.json: Item definitions and properties
- biomes.json: Biome definitions with parameters
- descriptions.json: Item description components
- monsters.json: Monster definitions and spawn rules
- prefixes.json: Quality-based item prefix definitions

## Save System
Game saves are stored in:
- Windows: `%APPDATA%/Adventure/save.json`