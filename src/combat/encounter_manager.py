import random
from .entity import Entity, EntityType, Stats
from ..engine.generics import load_json_config, calculate_distance

class EncounterManager:
    def __init__(self):
        self.monster_data = self._load_monsters()
        self.base_difficulty_radius = 100
        self.last_encounter_coords = None

    def _load_monsters(self) -> dict:
        data = load_json_config("monsters.json")
        for monster in data["monsters"].values():
            monster["rarity"]["base_rate"] = 0.01  # 1% base chance
            monster["rarity"]["min_distance"] = max(150, monster["rarity"]["min_distance"])
        return data["monsters"]

    def should_encounter(self, world_coords: tuple[int, int], biome: str) -> tuple[bool, str]:
        if self.last_encounter_coords:
            distance = calculate_distance(
                world_coords[0], world_coords[1],
                self.last_encounter_coords[0], self.last_encounter_coords[1]
            )
            if distance < 150:
                return False, None

        distance = calculate_distance(world_coords[0], world_coords[1], 0, 0)
        valid_monsters = [name for name, data in self.monster_data.items() 
                         if biome in data["biomes"]]

        for name in valid_monsters:
            monster = self.monster_data[name]
            if distance >= monster["rarity"]["min_distance"] and random.random() < monster["rarity"]["base_rate"]:
                self.last_encounter_coords = world_coords
                return True, name

        return False, None

    def generate_encounter(self, world_coords: tuple[int, int], biome: str) -> Entity:
        valid_monsters = [m for _, m in self.monster_data.items() 
                         if biome in m["biomes"]]
        if not valid_monsters:
            valid_monsters = list(self.monster_data.values())

        monster_data = random.choice(valid_monsters)
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
        return base_level + random.randint(-1, 1) + 1