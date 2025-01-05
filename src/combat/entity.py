import json
import os
import math
import random
from dataclasses import dataclass
from enum import Enum, auto

class EntityType(Enum):
    PLAYER = auto()
    MONSTER = auto()

@dataclass
class Stats:
    strength: int = 1
    defence: int = 1
    health: int = 10
    speed: int = 1
    stamina: int = 10
    dexterity: int = 1
    magic_power: int = 1
    magic_defence: int = 1
    wisdom: int = 1
    intelligence: int = 1

    def level_scale(self, level: int, meta_level: int):
        scale_factor = (level * 0.15 + meta_level * 0.1) / 10
        for attr in self.__dict__:
            current_value = getattr(self, attr)
            scaled_value = math.floor(current_value * (1 + scale_factor))
            setattr(self, attr, scaled_value)

class Entity:
    def __init__(self, name: str, entity_type: EntityType, level: int = 1):
        self.name = name
        self.entity_type = entity_type
        self.level = level
        self.meta_level = 0
        self.base_stats = Stats()
        self.current_stats = Stats()
        self.max_hp = 0
        self.current_hp = 0

    def initialize_stats(self):
        self.meta_level = self.calculate_meta_level()
        self.base_stats.level_scale(self.level, self.meta_level)
        self.current_stats = self.base_stats
        self.max_hp = self.calculate_max_hp()
        self.current_hp = self.max_hp

    def calculate_meta_level(self) -> int:
        stat_sum = sum(getattr(self.base_stats, stat) for stat in self.base_stats.__dict__)
        base_meta = stat_sum / 10
        level_factor = self.level / 20
        return max(1, round(base_meta * (1 + level_factor)))

    def calculate_max_hp(self) -> int:
        base_hp = self.base_stats.health * 4
        level_bonus = math.floor(self.level * 1.5)
        meta_bonus = self.meta_level * 2
        return base_hp + level_bonus + meta_bonus

class EncounterManager:
    def __init__(self):
        self.monster_data = self._load_monsters()
        self.base_difficulty_radius = 100
        self.last_encounter_coords = None

    def _load_monsters(self) -> dict:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(script_dir, "src", "config", "monsters.json"), "r", encoding="utf-8") as f:
            data = json.load(f)
            for monster in data["monsters"].values():
                monster["rarity"]["base_rate"] *= 0.04
                monster["rarity"]["min_distance"] = max(150, monster["rarity"]["min_distance"])
            return data["monsters"]

    def should_encounter(self, world_coords: tuple[int, int], biome: str) -> tuple[bool, str]:
        if self.last_encounter_coords:
            dx = world_coords[0] - self.last_encounter_coords[0]
            dy = world_coords[1] - self.last_encounter_coords[1]
            if math.sqrt(dx*dx + dy*dy) < 150:
                return False, None

        distance = math.sqrt(world_coords[0] ** 2 + world_coords[1] ** 2)
        valid_monsters = [name for name, data in self.monster_data.items() 
                         if biome in data["biomes"]]

        for name in valid_monsters:
            monster = self.monster_data[name]
            if distance >= monster["rarity"]["min_distance"] and random.random() < monster["rarity"]["base_rate"]:
                self.last_encounter_coords = world_coords
                return True, name

        return False, None

    def generate_encounter(self, world_coords: tuple[int, int], biome: str) -> Entity:
        valid_monsters = [m for m_name, m in self.monster_data.items() 
                         if biome in m["biomes"]]
        if not valid_monsters:
            valid_monsters = list(self.monster_data.values())

        monster_data = random.choice(valid_monsters)
        level = self.get_encounter_level(world_coords)
        
        monster = Entity(list(self.monster_data.keys())[list(self.monster_data.values()).index(monster_data)], 
                        EntityType.MONSTER, level)
        monster.base_stats = Stats(**monster_data["base_stats"])
        monster.initialize_stats()
        return monster

    def get_encounter_level(self, world_coords: tuple[int, int]) -> int:
        distance = math.sqrt(world_coords[0] ** 2 + world_coords[1] ** 2)
        base_level = max(1, int(distance / self.base_difficulty_radius * 20))
        return base_level