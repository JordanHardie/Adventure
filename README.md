# Adventure!

A procedurally generated roguelike game built with Python and Pygame featuring dynamic world generation, turn-based combat, and character progression.

## Features

- **Procedural World Generation**
  - Diverse biomes with unique characteristics
  - Dynamic terrain generation using Perlin noise
  - River and mountain systems
  - Climate simulation (temperature/humidity)

- **Combat System**
  - Turn-based strategic combat
  - Diverse monster types per biome
  - Dynamic encounter scaling
  - Loot generation system
  - Combat log with fade effects

- **Character System**
  - Stat-based character progression
  - Level-up system with skill points
  - Equipment system with quality tiers
  - Multiple equipment slots (armor, weapons, rings)
  - Inventory management with drag-and-drop

- **Game Systems**
  - Save/Load functionality
  - Multithreaded chunk loading
  - Font support management
  - UI system with multiple views

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run setup:
```bash
python setup.py install
```

## Project Structure

```
├── combat/
│   ├── combat_manager.py      # Combat mechanics and turns
│   ├── encounter_manager.py   # Monster spawning logic
│   ├── entity.py             # Base entity system
│   ├── loot_generator.py     # Item generation
│   ├── name_generator.py     # Item naming system
├── config/
│   ├── biomes.json           # Biome definitions
│   ├── descriptions.json     # Item descriptions
│   ├── font_config.py        # Font management
│   ├── font_support.json     # Character support
│   ├── game_config.py        # Game settings
│   ├── items.json           # Item definitions
│   ├── monsters.json        # Monster definitions
│   ├── prefixes.json        # Item quality prefixes
├── engine/
│   ├── core/
│   │   ├── display_manager.py    # Graphics rendering
│   │   ├── game_engine.py        # Core game loop
│   │   ├── game_state.py         # Game state management
│   │   ├── input_manager.py      # Input handling
│   │   ├── system_manager.py     # Game systems
│   │   └── ui_manager.py         # UI state management
│   ├── game_engine.py            # Main game initialization
│   ├── player.py                 # Player functionality
│   └── generics.py               # Utility functions
├── UI/
│   ├── combat_log_ui.py    # Combat messaging
│   ├── combat_ui.py        # Combat interface
│   ├── inventory_ui.py     # Inventory system
│   ├── level_up_ui.py      # Character progression
│   ├── loading_screen.py   # Loading interface
│   ├── menu.py            # Main menu system
├── world/
│   ├── terrain_generator.py # World generation
│   ├── world.py           # World management
│   ├── world_chunk.py     # Chunk data structure
```

## Technical Details

### World Generation
- Uses multiple layers of Perlin noise for terrain
- Implements threaded chunk generation
- Features biome determination based on climate factors
- Includes river system generation

### Combat System
- Turn-based combat with initiative system
- Stat-based damage calculation
- Critical hit system
- Dynamic monster scaling based on distance from origin

### Equipment System
- Quality-based item generation (0-4 tiers)
- Procedural item naming
- Stat scaling based on quality and level
- Multiple equipment slots with unique bonuses

### Save System
Save files are stored in:
- Windows: `%APPDATA%/Adventure/save.json`

## Contributing

See the GitHub repository for contribution guidelines.

## License

This project is licensed under the MPL 2.0 License - see the LICENSE file for details.
