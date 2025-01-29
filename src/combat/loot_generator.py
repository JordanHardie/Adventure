from .name_generator import NameGenerator
from typing import Optional, Dict, List, Tuple
from ..engine.player import Item, ItemType, ItemStats
from ..engine.generics import load_json_config, RandomUtils

class LootGenerator:
    BASE_GOLD = 10
    BASE_ITEM_CHANCE = 0.1
    QUALITY_WEIGHTS = [50, 30, 15, 4, 1]  # Weights for qualities 0-4

    def __init__(self):
        self.items_data = load_json_config("items.json")
        self.name_generator = NameGenerator()

    def calculate_quality(self, monster_level: int, meta_level: int) -> int:
        quality_chance = (monster_level + meta_level) / 100
        weights = self.QUALITY_WEIGHTS[:]
        for i, weight in enumerate(weights):
            weights[i] = weight * (1 + quality_chance) ** i
        return RandomUtils.choices(range(5), weights=weights)[0]

    def _generate_item(self, monster_level: int, meta_level: int) -> Optional[Item]:
        categories = [('weapons', 0.3), ('armor', 0.5), ('rings', 0.2)]
        category = RandomUtils.choices(
            [c[0] for c in categories], 
            weights=[c[1] for c in categories]
        )[0]

        try:
            if category == 'weapons':
                item_name, item_data = RandomUtils.choice(list(self.items_data['weapons'].items()))
                item_type = getattr(ItemType, item_data['slot'])
                base_name = item_name
                stats = item_data['base_stats']
            elif category == 'rings':
                item_name, item_data = RandomUtils.choice(list(self.items_data['rings'].items()))
                item_type = getattr(ItemType, item_data['slot'])
                base_name = item_name
                stats = item_data['base_stats']
            else:
                armor_type = RandomUtils.choice(list(self.items_data['armor'].keys()))
                piece_name, piece_data = RandomUtils.choice(list(self.items_data['armor'][armor_type].items()))
                item_type = getattr(ItemType, piece_data['slot'])
                base_name = f"{armor_type} {piece_name}"
                stats = piece_data['base_stats']

            quality = self.calculate_quality(monster_level, meta_level)
            item_stats = self._calculate_stats(stats, quality, monster_level)
            name = self.name_generator.generate_name(base_name, quality)
        
            return Item(name, item_type, quality, item_stats)
        
        except Exception as e:
            print(f"Error generating item: {str(e)}")
            return None

    def _calculate_stats(
        self, base_stats: Dict, quality: int, monster_level: int
    ) -> ItemStats:
        stat_multiplier = 1 + (quality * 0.2) + (monster_level * 0.1)

        item_stats = ItemStats()
        for stat, value in base_stats.items():
            setattr(item_stats, stat, int(value * stat_multiplier))

        return item_stats

    def generate_loot(self, monster_level: int, meta_level: int) -> Tuple[List[Item], int]:
        items = []
        gold = int(self.BASE_GOLD * (1 + monster_level * 0.5 + meta_level * 0.2))
        gold_variation = gold // 4
        gold += RandomUtils.int(-gold_variation, gold_variation)

        if RandomUtils.chance(1.0):  # Always generate item for now
            if item := self._generate_item(monster_level, meta_level):
                items.append(item)

        return items, gold