import random
import math
import json
import os
from .entity import Entity, EntityType, Stats
from ..engine.player import Item, ItemType, ItemStats

class LootGenerator:
    BASE_GOLD = 10
    BASE_ITEM_CHANCE = 0.3
    QUALITY_WEIGHTS = [50, 30, 15, 4, 1]  # Weights for qualities 0-4

    @staticmethod
    def generate_loot(monster_level: int, meta_level: int) -> tuple[list[Item], int]:
        items = []
        gold = int(LootGenerator.BASE_GOLD * (1 + monster_level * 0.5 + meta_level * 0.2))
        gold += random.randint(-gold//4, gold//4)
        
        item_chance = LootGenerator.BASE_ITEM_CHANCE * (1 + meta_level/50)
        
        if random.random() < item_chance:
            quality_chance = (monster_level + meta_level) / 100
            weights = LootGenerator.QUALITY_WEIGHTS[:]
            for i in range(len(weights)):
                weights[i] *= (1 + quality_chance) ** i
            
            quality = random.choices(range(5), weights=weights)[0]
            base_stat = quality * 2 + (monster_level + meta_level) // 10
            stats = ItemStats(**{stat: max(0, base_stat + random.randint(-2, 2)) 
                             for stat in ItemStats().__dict__})
            
            item_type = random.choice(list(ItemType))
            if item_type not in [ItemType.POTION, ItemType.GOLD]:
                items.append(Item(item_type.name.capitalize(), item_type, quality, stats))

        return items, gold

class EncounterManager:
    def __init__(self):
        self.monster_data = self._load_monsters()
        self.base_difficulty_radius = 100
        self.last_encounter_coords = None

    def _load_monsters(self) -> dict:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(script_dir, "src", "config", "monsters.json"), "r") as f:
            data = json.load(f)
            for monster in data["monsters"].values():
                monster["rarity"]["base_rate"] = 0.01  # 1% base chance
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
        base_level = max(1, int(distance / (self.base_difficulty_radius * 5)))
        return base_level + random.randint(-1, 1)

class CombatManager:
    def __init__(self):
        self.current_encounter = None
        self.turn_order = []

    def start_combat(self, player: Entity, monster: Entity):
        self.current_encounter = (player, monster)
        self.determine_turn_order()

    def determine_turn_order(self):
        player, monster = self.current_encounter
        self.turn_order = sorted([player, monster], 
                               key=lambda x: x.current_stats.speed, reverse=True)

    def calculate_damage(self, attacker: Entity, defender: Entity, 
                        is_magical: bool = False) -> int:
        if is_magical:
            attack = attacker.current_stats.magic_power
            defence = defender.current_stats.magic_defence
        else:
            attack = attacker.current_stats.strength
            defence = defender.current_stats.defence

        base_damage = max(1, attack - defence // 2)
        crit_chance = attacker.current_stats.dexterity * 0.05
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
            "loot": None
        }

        if action == "attack":
            damage = self.calculate_damage(attacker, defender)
            defender.current_hp -= damage
            result["damage_dealt"] = damage
            result["message"] = f"{attacker.name} attacks for {damage} damage!"

            if defender.current_hp <= 0 and defender.entity_type == EntityType.MONSTER:
                items, gold = LootGenerator.generate_loot(defender.level, defender.meta_level)
                result["loot"] = {"items": items, "gold": gold}

        return result