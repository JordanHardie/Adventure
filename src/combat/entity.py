from dataclasses import dataclass
from enum import Enum, auto
import random
import math

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
        scale_factor = (level + meta_level) / 20
        for attr in self.__dict__:
            current_value = getattr(self, attr)
            scaled_value = math.floor(current_value * scale_factor)
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
        self.experience = 0

    def calculate_meta_level(self) -> int:
        """Calculate meta-level based on base stats and current level"""
        stat_sum = sum(
            getattr(self.base_stats, stat) for stat in self.base_stats.__dict__
        )
        base_meta = stat_sum / 10  # Base meta-level from stats
        level_factor = self.level / 20  # Level contribution
        return max(1, round(base_meta * (1 + level_factor)))

    def initialize_stats(self):
        self.meta_level = self.calculate_meta_level()
        self.base_stats.level_scale(self.level, self.meta_level)
        self.current_stats = self.base_stats
        self.max_hp = self.calculate_max_hp()
        self.current_hp = self.max_hp

    def calculate_max_hp(self) -> int:
        return (self.base_stats.health * 10) + (self.level * 5) + (self.meta_level * 10)


class MonsterTemplate:
    def __init__(
        self,
        name: str,
        meta_level: int,
        biomes: list[str],
        base_stats: Stats,
        rarity: dict,
    ):
        self.name = name
        self.meta_level = meta_level
        self.biomes = biomes
        self.base_stats = base_stats
        self.rarity = rarity

    def create_instance(self, level: int) -> Entity:
        monster = Entity(self.name, EntityType.MONSTER, level)
        monster.base_stats = self.base_stats
        monster.initialize_stats()
        return monster


class EncounterManager:
    def __init__(self):
        self.monster_templates = self._load_monster_templates()
        self.base_difficulty_radius = 100

    def _load_monster_templates(self) -> dict:
        # This would normally load from a JSON file
        templates = {}

        # Example monster templates
        templates["Slime"] = MonsterTemplate(
            "Slime",
            meta_level=30,
            biomes=["grassland", "forest", "swamp"],
            base_stats=Stats(
                strength=3,
                defence=2,
                health=5,
                speed=2,
                stamina=10,
                dexterity=1,
                magic_power=1,
                magic_defence=1,
                wisdom=1,
                intelligence=1,
            ),
            rarity={"base_rate": 0.25, "min_distance": 0},
        )

        templates["Dragon"] = MonsterTemplate(
            "Dragon",
            meta_level=80,
            biomes=["mountain", "volcanic", "snowy_peaks"],
            base_stats=Stats(
                strength=15,
                defence=12,
                health=50,
                speed=8,
                stamina=30,
                dexterity=7,
                magic_power=12,
                magic_defence=10,
                wisdom=8,
                intelligence=8,
            ),
            rarity={"base_rate": 0.01, "min_distance": 500},
        )

        return templates

    def calculate_encounter_chance(self, monster_name: str, distance: float) -> float:
        monster_template = self.monster_templates[monster_name]
        if distance < monster_template.rarity["min_distance"]:
            return 0

        base_rate = monster_template.rarity["base_rate"]
        distance_factor = math.log(1 + distance / self.base_difficulty_radius)

        if monster_template.meta_level > 50:  # For high-tier monsters
            return base_rate * distance_factor
        return base_rate

    def should_encounter(
        self, world_coords: tuple[int, int], biome: str
    ) -> tuple[bool, str]:
        distance = math.sqrt(world_coords[0] ** 2 + world_coords[1] ** 2)

        # Get valid monsters for this biome
        valid_monsters = [
            name
            for name, template in self.monster_templates.items()
            if biome in template.biomes
        ]

        # Calculate chances for each valid monster
        chances = {
            name: self.calculate_encounter_chance(name, distance)
            for name in valid_monsters
        }

        # Roll for each monster type
        for name, chance in chances.items():
            if random.random() < chance:
                return True, name

        return False, None

    def get_encounter_level(self, world_coords: tuple[int, int]) -> int:
        distance = math.sqrt(world_coords[0] ** 2 + world_coords[1] ** 2)
        # Base level starts at 1 and scales with distance
        base_level = max(1, int(distance / self.base_difficulty_radius * 20))
        # Add some randomness to the level
        return base_level + random.randint(-2, 2)

    def generate_encounter(self, world_coords: tuple[int, int], biome: str) -> Entity:
        # Filter monsters by biome
        valid_monsters = [
            m for m in self.monster_templates.values() if biome in m.biomes
        ]
        if not valid_monsters:
            # Fallback to any monster if none available for this biome
            valid_monsters = list(self.monster_templates.values())

        monster_template = random.choice(valid_monsters)
        level = self.get_encounter_level(world_coords)
        return monster_template.create_instance(level)


class CombatManager:
    def __init__(self):
        self.current_encounter = None
        self.turn_order = []

    def start_combat(self, player: Entity, monster: Entity):
        self.current_encounter = (player, monster)
        self.determine_turn_order()

    def determine_turn_order(self):
        player, monster = self.current_encounter
        self.turn_order = sorted(
            [player, monster], key=lambda x: x.current_stats.speed, reverse=True
        )

    def calculate_damage(
        self, attacker: Entity, defender: Entity, is_magical: bool = False
    ) -> int:
        if is_magical:
            attack = attacker.current_stats.magic_power
            defence = defender.current_stats.magic_defence
        else:
            attack = attacker.current_stats.strength
            defence = defender.current_stats.defence

        base_damage = max(1, attack - defence // 2)

        # Critical hit chance based on dexterity
        crit_chance = attacker.current_stats.dexterity * 0.05  # 5% per point
        is_crit = random.random() < crit_chance

        if is_crit:
            base_damage *= 2

        return base_damage

    def process_turn(self, attacker: Entity, defender: Entity, action: str) -> dict:
        result = {
            "damage_dealt": 0,
            "is_critical": False,
            "status_effects": [],
            "message": "",
        }

        if action == "attack":
            damage = self.calculate_damage(attacker, defender)
            defender.current_hp -= damage
            result["damage_dealt"] = damage
            result["message"] = f"{attacker.name} attacks for {damage} damage!"

        return result
