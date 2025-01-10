from .entity import Entity, EntityType, Stats
from ..engine.generics import calculate_distance, RandomUtils, load_json_config

class EncounterManager:
    def __init__(self):
        self.monster_data = self._load_monsters()
        self.base_difficulty_radius = 100
        self.last_encounter_coords = None

    def _load_monsters(self):
        monsters_config = load_json_config("monsters.json")
        return monsters_config["monsters"]

    def should_encounter(self, world_coords: tuple[int, int], biome: str) -> tuple[bool, str]:
        # Check if we're too close to the last encounter
        if self.last_encounter_coords:
            distance_from_last = calculate_distance(
                world_coords[0], world_coords[1],
                self.last_encounter_coords[0], self.last_encounter_coords[1]
            )
            if distance_from_last < 150:  # Minimum tiles between encounters
                return False, None

        # Check distance from origin
        distance_from_origin = calculate_distance(world_coords[0], world_coords[1], 0, 0)
    
        valid_monsters = []
        for name, data in self.monster_data.items():
            if (biome in data["biomes"] and 
                distance_from_origin >= data["rarity"]["min_distance"]):
                valid_monsters.append(name)

        if not valid_monsters:
            return False, None

        for name in valid_monsters:
            monster = self.monster_data[name]
            if RandomUtils.chance(monster["rarity"]["base_rate"] * 0.1):  # Reduced chance
                self.last_encounter_coords = world_coords
                return True, name

        return False, None

    def generate_encounter(self, world_coords: tuple[int, int], biome: str) -> Entity:
        valid_monsters = [m for _, m in self.monster_data.items() 
                         if biome in m["biomes"]]
        if not valid_monsters:
            valid_monsters = list(self.monster_data.values())

        monster_data = RandomUtils.choice(valid_monsters)
        level = self.get_encounter_level(world_coords)
        
        monster = Entity(
            list(self.monster_data.keys())[list(self.monster_data.values()).index(monster_data)], 
            EntityType.MONSTER,
            level
        )
        monster.base_stats = Stats(**monster_data["base_stats"])
        monster.initialize_stats()
        return monster

    def get_encounter_level(self, world_coords: tuple[int, int]) -> int:
        distance = calculate_distance(world_coords[0], world_coords[1], 0, 0)
        base_level = max(1, int(distance / (self.base_difficulty_radius * 5)))
        return base_level + RandomUtils.int(-1, 1) + 1