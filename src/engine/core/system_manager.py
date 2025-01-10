from typing import List
from ...engine.player import Entity
from ...engine.generics import save_game_data
from ...combat.combat_manager import CombatManager
from ...combat.encounter_manager import EncounterManager

class GameSystem:
    def update(self, _) -> None:
        pass

class CombatSystem(GameSystem):
    def __init__(self):
        self.combat_manager = CombatManager()

    def update(self, game_state) -> None:
        """No updates needed per frame for combat system"""
        pass

    def process_turn(self, player: Entity, enemy: Entity, action: str) -> dict:
        return self.combat_manager.process_turn(player, enemy, action)

class EncounterSystem(GameSystem):
    def __init__(self):
        self.encounter_manager = EncounterManager()
        
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
            game_state.current_enemy = self.encounter_manager.generate_encounter(coords, biome)
            game_state.systems.combat_system.combat_manager.start_combat(
                game_state.player, 
                game_state.current_enemy
            )
            game_state.transition_to("combat")

class SaveSystem(GameSystem):
    def update(self, game_state) -> None:
        if game_state.current_state == "game":
            # Autosave every N updates
            save_game_data({
                'x': game_state.player.x, 
                'y': game_state.player.y
            })

class ProgressionSystem(GameSystem):
    def update(self, game_state) -> None:
        if game_state.current_state == "game":
            # Handle any ongoing progression updates
            pass

class SystemManager:
    def __init__(self):
        self.combat_system = CombatSystem()
        self.encounter_system = EncounterSystem()
        self.save_system = SaveSystem()
        self.progression_system = ProgressionSystem()
        
        self.systems: List[GameSystem] = [
            self.combat_system,
            self.encounter_system,
            self.save_system,
            self.progression_system
        ]
    
    def update(self, game_state) -> None:
        for system in self.systems:
            system.update(game_state)