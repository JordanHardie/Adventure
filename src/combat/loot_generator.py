import random
from typing import Optional, Dict, List, Tuple
from ..engine.player import Item, ItemType, ItemStats
from .name_generator import NameGenerator
from ..engine.generics import load_json_config

class LootGenerator:
    BASE_GOLD = 10
    BASE_ITEM_CHANCE = 0.9
    QUALITY_WEIGHTS = [50, 30, 15, 4, 1]  # Weights for qualities 0-4

    def __init__(self):
        self.items_data = load_json_config("items.json")
        self.name_generator = NameGenerator()

    def _generate_item(self, monster_level: int, meta_level: int) -> Optional[Item]:
        categories = [('weapons', 0.3), ('armor', 0.5), ('rings', 0.2)]
        category = random.choices([c[0] for c in categories], weights=[c[1] for c in categories])[0]
        
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

        quality = self._calculate_quality(monster_level, meta_level)
        item_stats = self._calculate_stats(template[1]['base_stats'], quality, monster_level)
        
        name = self.name_generator.generate_name(base_name, quality)
        
        return Item(name, item_type, quality, item_stats)

    def _calculate_quality(self, monster_level: int, meta_level: int) -> int:
        quality_chance = (monster_level + meta_level) / 100
        weights = self.QUALITY_WEIGHTS[:]
        for i in range(len(weights)):
            weights[i] *= (1 + quality_chance) ** i
        
        return random.choices(range(5), weights=weights)[0]

    def _calculate_stats(self, base_stats: Dict, quality: int, monster_level: int) -> ItemStats:
        stat_multiplier = 1 + (quality * 0.2) + (monster_level * 0.1)
        
        item_stats = ItemStats()
        for stat, value in base_stats.items():
            setattr(item_stats, stat, int(value * stat_multiplier))
            
        return item_stats

    def generate_loot(self, monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
        items = []
        gold = int(self.BASE_GOLD * (1 + monster_level * 0.5 + meta_level * 0.2))
        gold += random.randint(-gold//4, gold//4)
        
        item_chance = self.BASE_ITEM_CHANCE * (1 + meta_level/50)
        
        if random.random() < item_chance:
            if item := self._generate_item(monster_level, meta_level):
                items.append(item)

        return items, gold