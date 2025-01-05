import os
import math
import json
import random
from .name_generator import NameGenerator
from typing import List, Tuple, Dict, Optional
from ..combat.entity import Entity, EntityType, Stats
from ..engine.player import Item, ItemType, ItemStats

class LootGenerator:
    """Generates loot drops from monsters based on their level and meta-level."""
    
    BASE_GOLD = 10
    BASE_ITEM_CHANCE = 0.3
    QUALITY_WEIGHTS = [50, 30, 15, 4, 1]  # Weights for qualities 0-4

    def __init__(self):
        self.items_data = self._load_item_data()
        self.suffixes = self._load_suffixes()

    def _load_item_data(self) -> Dict:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(script_dir, "src", "config", "items.json"), "r") as f:
            return json.load(f)

    def _load_suffixes(self) -> Dict:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(script_dir, "src", "config", "prefixes.json"), "r") as f:
            return json.load(f)

    def _generate_item(self, monster_level: int, meta_level: int) -> Optional[Item]:
        """Generate a random item based on monster level."""
        # Determine item category
        categories = [
            ('weapons', 0.3),
            ('armor', 0.5),
            ('rings', 0.2)
        ]
        
        category = random.choices([c[0] for c in categories], weights=[c[1] for c in categories])[0]
        
        # Select template
        if category == 'weapons':
            template = random.choice(list(self.items_data['weapons'].items()))
            item_type = getattr(ItemType, template[1]['slot'])
            base_name = template[0]
        elif category == 'rings':
            template = random.choice(list(self.items_data['rings'].items()))
            item_type = getattr(ItemType, template[1]['slot'])
            base_name = template[0]
        else:
            armor_type = random.choice(list(self.items_data['armor'].keys()))
            piece = random.choice(list(self.items_data['armor'][armor_type].items()))
            template = piece[1]
            item_type = getattr(ItemType, template['slot'])
            base_name = f"{armor_type} {piece[0]}"

        # Calculate quality and stats
        quality = self._calculate_quality(monster_level, meta_level)
        item_stats = self._calculate_stats(template[1]['base_stats'], quality, monster_level)
        
        # Generate name
        name = NameGenerator.generate_name(base_name, template[1]['base_stats'], quality)
        
        return Item(name, item_type, quality, item_stats)

    def _calculate_quality(self, monster_level: int, meta_level: int) -> int:
        """Calculate item quality based on monster stats."""
        quality_chance = (monster_level + meta_level) / 100
        weights = self.QUALITY_WEIGHTS[:]
        for i in range(len(weights)):
            weights[i] *= (1 + quality_chance) ** i
        
        return random.choices(range(5), weights=weights)[0]

    def _calculate_stats(self, base_stats: Dict, quality: int, monster_level: int) -> ItemStats:
        """Calculate final item stats based on quality and level."""
        stat_multiplier = 1 + (quality * 0.2) + (monster_level * 0.1)
        
        item_stats = ItemStats()
        for stat, value in base_stats.items():
            setattr(item_stats, stat, int(value * stat_multiplier))
            
        return item_stats

    def generate_loot(self, monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
        """Generate loot including items and gold."""
        items = []
        gold = int(self.BASE_GOLD * (1 + monster_level * 0.5 + meta_level * 0.2))
        gold += random.randint(-gold//4, gold//4)
        
        item_chance = self.BASE_ITEM_CHANCE * (1 + meta_level/50)
        
        if random.random() < item_chance:
            if item := self._generate_item(monster_level, meta_level):
                items.append(item)

        return items, gold

    @staticmethod
    def generate_loot(monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
        """Static method for backward compatibility."""
        loot_gen = LootGenerator()
        return loot_gen.generate_loot(monster_level, meta_level)

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

        import os
        import math
        import json
        import random
        from .name_generator import NameGenerator
        from typing import List, Tuple, Dict, Optional
        from ..combat.entity import Entity, EntityType, Stats
        from ..engine.player import Item, ItemType, ItemStats

        class LootGenerator:
            """Generates loot drops from monsters based on their level and meta-level."""
            
            BASE_GOLD = 10
            BASE_ITEM_CHANCE = 0.3
            QUALITY_WEIGHTS = [50, 30, 15, 4, 1]  # Weights for qualities 0-4

            def __init__(self):
                self.items_data = self._load_item_data()
                self.prefixes = self._load_prefixes()

            def _load_item_data(self) -> Dict:
                script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                with open(os.path.join(script_dir, "src", "config", "items.json"), "r") as f:
                    return json.load(f)

            def _load_prefixes(self) -> Dict:
                script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                with open(os.path.join(script_dir, "src", "config", "prefixes.json"), "r") as f:
                    return json.load(f)

            def _generate_item(self, monster_level: int, meta_level: int) -> Optional[Item]:
                """Generate a random item based on monster level."""
                # Determine item category
                categories = [
                    ('weapons', 0.3),
                    ('armor', 0.5),
                    ('rings', 0.2)
                ]
                
                category = random.choices([c[0] for c in categories], weights=[c[1] for c in categories])[0]
                
                # Select template
                if category == 'weapons':
                    template = random.choice(list(self.items_data['weapons'].items()))
                    item_type = getattr(ItemType, template[1]['slot'])
                    base_name = template[0]
                elif category == 'rings':
                    template = random.choice(list(self.items_data['rings'].items()))
                    item_type = getattr(ItemType, template[1]['slot'])
                    base_name = template[0]
                else:
                    armor_type = random.choice(list(self.items_data['armor'].keys()))
                    piece = random.choice(list(self.items_data['armor'][armor_type].items()))
                    template = piece[1]
                    item_type = getattr(ItemType, template['slot'])
                    base_name = f"{armor_type} {piece[0]}"

                # Calculate quality and stats
                quality = self._calculate_quality(monster_level, meta_level)
                item_stats = self._calculate_stats(template[1]['base_stats'], quality, monster_level)
                
                # Generate name
                name = NameGenerator.generate_name(base_name, template[1]['base_stats'], quality)
                
                return Item(name, item_type, quality, item_stats)

            def _calculate_quality(self, monster_level: int, meta_level: int) -> int:
                """Calculate item quality based on monster stats."""
                quality_chance = (monster_level + meta_level) / 100
                weights = self.QUALITY_WEIGHTS[:]
                for i in range(len(weights)):
                    weights[i] *= (1 + quality_chance) ** i
                
                return random.choices(range(5), weights=weights)[0]

            def _calculate_stats(self, base_stats: Dict, quality: int, monster_level: int) -> ItemStats:
                """Calculate final item stats based on quality and level."""
                stat_multiplier = 1 + (quality * 0.2) + (monster_level * 0.1)
                
                item_stats = ItemStats()
                for stat, value in base_stats.items():
                    setattr(item_stats, stat, int(value * stat_multiplier))
                    
                return item_stats

            def generate_loot(self, monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
                """Generate loot including items and gold."""
                items = []
                gold = int(self.BASE_GOLD * (1 + monster_level * 0.5 + meta_level * 0.2))
                gold += random.randint(-gold//4, gold//4)
                
                item_chance = self.BASE_ITEM_CHANCE * (1 + meta_level/50)
                
                if random.random() < item_chance:
                    if item := self._generate_item(monster_level, meta_level):
                        items.append(item)

                return items, gold

            @staticmethod
            def generate_loot(monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
                """Static method for backward compatibility."""
                loot_gen = LootGenerator()
                return loot_gen.generate_loot(monster_level, meta_level)

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

        return result