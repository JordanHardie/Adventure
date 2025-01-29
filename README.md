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
├── src/
│   ├── combat/
│   │   ├── combat_manager.py    # Combat system and turns
│   │   ├── encounter_manager.py # Monster spawning
│   │   ├── entity.py           # Base entities (player/monsters)
│   │   ├── loot_generator.py   # Item generation
│   │   ├── monster_ai.py       # Monster behavior
│   │   ├── name_generator.py   # Item naming
│   │   ├── skill_tree.py       # Character progression
│   │   └── skills.py           # Skill definitions
│   ├── config/
│   │   ├── biomes.json         # Biome definitions
│   │   ├── descriptions.json   # Item descriptions
│   │   ├── font_config.py      # Font management
│   │   ├── font_support.json   # Character support
│   │   ├── game_config.py      # Game settings
│   │   ├── items.json         # Item definitions
│   │   ├── monsters.json      # Monster definitions
│   │   └── prefixes.json      # Item quality prefixes
│   ├── engine/
│   │   ├── core/
│   │   │   ├── display_manager.py  # Graphics
│   │   │   ├── game_state.py      # Game state
│   │   │   ├── input_manager.py    # Input handling
│   │   │   ├── system_manager.py   # Game systems
│   │   │   └── ui_manager.py       # UI states
│   │   ├── generics.py         # Utilities
│   │   └── player.py           # Player class
│   ├── UI/
│   │   ├── combat_log_ui.py    # Combat messages
│   │   ├── combat_ui.py        # Combat interface
│   │   ├── inventory_ui.py     # Inventory
│   │   ├── level_up_ui.py      # Level up menu
│   │   ├── loading_screen.py   # Loading UI
│   │   ├── menu.py            # Main menu
│   │   └── skill_tree_ui.py   # Skill tree
│   └── world/
│       ├── terrain_generator.py # World generation
│       ├── world.py           # World management
│       └── world_chunk.py     # Chunk system
├── build.py                    # Build script
├── main.py                     # Entry point
├── README.md                   # Documentation
└── setup.py                    # Package config
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
