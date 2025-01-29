from .entity import Entity, EntityType, Stats
from ..engine.generics import calculate_distance, RandomUtils, load_json_config

class EncounterManager:
    def __init__(self):
        self.monster_data = self._load_monsters()
        self.base_difficulty_radius = 100
        self.last_encounter_coords = None

    @staticmethod
    def _load_monsters():
        monsters_config = load_json_config("monsters.json")
        return monsters_config["monsters"]

    def _generate_base_stats(self, monster_data: dict, level: int) -> Stats:
        stat_focus = monster_data["stat_focus"]
        base_stats = {}

        # Base values: primary stats (8-12), secondary (5-8), weak (2-4)
        for stat in ["strength", "defence", "health", "speed", "stamina", "magic_power", "magic_defence", "wisdom",
                     "intelligence"]:
            if stat in stat_focus["primary"]:
                base_stats[stat] = RandomUtils.int(8, 12)
            elif stat in stat_focus["secondary"]:
                base_stats[stat] = RandomUtils.int(5, 8)
            elif stat in stat_focus["weak"]:
                base_stats[stat] = RandomUtils.int(2, 4)
            else:
                base_stats[stat] = RandomUtils.int(4, 6)

        # Health gets special scaling
        base_stats["health"] *= 1.01

        # Scale with level
        scale_factor = 1 + (level * 0.15)
        for stat in base_stats:
            base_stats[stat] = int(base_stats[stat] * scale_factor)

        return Stats(**base_stats)

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
        try:
            valid_monsters = [m for _, m in self.monster_data.items() if biome in m["biomes"]]
            monster_data = RandomUtils.choice(valid_monsters)
            level = self.get_encounter_level(world_coords)

            monster = Entity(
                list(self.monster_data.keys())[list(self.monster_data.values()).index(monster_data)],
                EntityType.MONSTER,
                level
            )

            monster.base_stats = self._generate_base_stats(monster_data, level)
            monster.initialize_stats()
            return monster
        except Exception as e:
            print(f"ERROR generating encounter: {str(e)}")
            raise

    def get_encounter_level(self, world_coords: tuple[int, int]) -> int:
        distance = calculate_distance(world_coords[0], world_coords[1], 0, 0)
        base_level = max(1, int(distance / (self.base_difficulty_radius * 5)))
        return base_level + RandomUtils.int(-1, 1) + 1