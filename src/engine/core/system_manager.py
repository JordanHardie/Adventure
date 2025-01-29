"""
Core game systems management module.
Handles initialization and coordination of game subsystems.
"""

from typing import Dict, Type
from ...combat.skill_tree import SkillTree
from ...combat.combat_manager import CombatManager
from ...combat.encounter_manager import EncounterManager
from .services import ConfigService, with_error_handling

class GameSystem:
    """Base class for all game systems."""

    def __init__(self):
        self.config = ConfigService()
        self.logger = self.config.logger

    @with_error_handling
    def update(self, game_state) -> None:
        """Update system state. Override in subclasses."""
        pass

    def cleanup(self) -> None:
        """Clean up system resources. Override if needed."""
        pass

class CombatSystem(GameSystem):
    """Handles combat-related mechanics and state."""

    def __init__(self):
        super().__init__()
        self.combat_manager = CombatManager()
        self.skill_tree = SkillTree()
        self.logger.debug("Combat system initialized")

    @with_error_handling
    def process_turn(self, player, enemy, action: str) -> dict:
        return self.combat_manager.process_turn(player, enemy, action)


class EncounterSystem(GameSystem):
    """Manages monster encounters and spawning."""

    def __init__(self):
        super().__init__()
        self.encounter_manager = EncounterManager()
        self.logger.debug("Encounter system initialized")

    @with_error_handling
    def check_encounters(self, game_state) -> None:
        if game_state.current_state != "game":
            return

        coords = (game_state.player.x, game_state.player.y)
        chunk = game_state.world.get_chunk(
            coords[0] // game_state.world.chunk_size,
            coords[1] // game_state.world.chunk_size
        )

        local_x = coords[0] % game_state.world.chunk_size
        local_y = coords[1] % game_state.world.chunk_size
        biome = chunk.get_biome(local_x, local_y)

        should_encounter, monster_name = self.encounter_manager.should_encounter(coords, biome)

        if should_encounter and monster_name:
            self.logger.info(f"Triggering encounter with {monster_name} in {biome}")
            game_state.current_enemy = self.encounter_manager.generate_encounter(coords, biome)
            game_state.systems.combat_system.combat_manager.start_combat(
                game_state.player,
                game_state.current_enemy
            )
            game_state.transition_to("combat")


class SaveSystem(GameSystem):
    """Handles game save/load operations."""

    @with_error_handling
    def update(self, game_state) -> None:
        if game_state.current_state == "game":
            from ...engine.generics import save_game_data
            save_game_data({
                'x': game_state.player.x,
                'y': game_state.player.y
            })
            self.logger.debug("Game state autosaved")


class ProgressionSystem(GameSystem):
    """Manages character progression and leveling."""

    @with_error_handling
    def update(self, game_state) -> None:
        if game_state.current_state == "game":
            self._check_level_up(game_state)

    def _check_level_up(self, game_state) -> None:
        if game_state.player.experience >= game_state.player.next_level_exp:
            old_level = game_state.player.level
            game_state.player.level_up()
            self.logger.info(f"Player leveled up from {old_level} to {game_state.player.level}")


class SystemManager:
    """Manages all game systems and their lifecycle."""

    def __init__(self):
        self.config = ConfigService()
        self.logger = self.config.logger
        self.logger.info("Initializing game systems")

        self.systems: Dict[str, GameSystem] = {}
        self._init_systems()

    @with_error_handling
    def _init_systems(self) -> None:
        """Initialize all game systems."""
        system_classes: Dict[str, Type[GameSystem]] = {
            'combat': CombatSystem,
            'encounter': EncounterSystem,
            'save': SaveSystem,
            'progression': ProgressionSystem
        }

        for name, system_class in system_classes.items():
            try:
                self.systems[name] = system_class()
                self.logger.debug(f"Initialized {name} system")
            except Exception as e:
                self.logger.error(f"Failed to initialize {name} system: {str(e)}")
                raise

        # Store commonly accessed systems as properties
        self.combat_system = self.systems['combat']
        self.encounter_system = self.systems['encounter']

    @with_error_handling
    def update(self, game_state) -> None:
        """Update all game systems."""
        for system_name, system in self.systems.items():
            try:
                system.update(game_state)
            except Exception as e:
                self.logger.error(f"Error updating {system_name} system: {str(e)}")
                raise

    def cleanup(self) -> None:
        """Clean up all systems."""
        self.logger.info("Cleaning up game systems")
        for system_name, system in self.systems.items():
            try:
                system.cleanup()
                self.logger.debug(f"Cleaned up {system_name} system")
            except Exception as e:
                self.logger.error(f"Error cleaning up {system_name} system: {str(e)}")