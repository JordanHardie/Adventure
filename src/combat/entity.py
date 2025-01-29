from enum import Enum, auto
from dataclasses import dataclass

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
            scaled_value = max(1, int(current_value * (1 + scale_factor)))
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
        base_hp = self.base_stats.health * 2
        level_bonus = int(self.level * 1.5)
        meta_bonus = self.meta_level * 2
        return base_hp + level_bonus + meta_bonus