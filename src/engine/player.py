import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, List
from ..engine.generics import load_json_config
from ..combat.entity import Entity, EntityType, Stats

class ItemType(Enum):
    HELMET = auto()
    TORSO = auto()
    BRACERS = auto()
    GLOVES = auto()
    RING = auto()
    LEGS = auto()
    FEET = auto()
    POTION = auto()
    GOLD = auto()
    WEAPON = auto()

@dataclass
class ItemStats(Stats):
    pass

class Item:
    def __init__(self, name: str, item_type: ItemType, quality: int, stats: ItemStats):
        self.name = name
        self.item_type = item_type
        self.quality = quality  # 0-4, matching prefixes.json
        self.stats = stats
        self.prefixes = load_json_config("prefixes.json")
        self.full_name = name

    def _get_random_prefix(self) -> str:
        return random.choice(self.prefixes[str(self.quality)])

class Inventory:
    def __init__(self):
        self.equipped: Dict[ItemType, Optional[Item]] = {
            ItemType.HELMET: None,
            ItemType.TORSO: None,
            ItemType.BRACERS: None,
            ItemType.GLOVES: None,
            ItemType.LEGS: None,
            ItemType.FEET: None,
        }
        self.rings: List[Optional[Item]] = [None] * 10
        self.items: List[Item] = []
        self.gold = 0
        
    def equip(self, item: Item, slot: Optional[int] = None) -> Optional[Item]:
        if item.item_type == ItemType.RING:
            if slot is None or slot >= 10:
                return None
            old_item = self.rings[slot]
            self.rings[slot] = item
            return old_item
        
        old_item = self.equipped.get(item.item_type)
        self.equipped[item.item_type] = item
        return old_item

    def unequip(self, item_type: ItemType, slot: Optional[int] = None) -> Optional[Item]:
        if item_type == ItemType.RING:
            if slot is None or slot >= 10:
                return None
            item = self.rings[slot]
            self.rings[slot] = None
            return item
        
        item = self.equipped.get(item_type)
        self.equipped[item_type] = None
        return item

    def get_total_stats(self) -> ItemStats:
        total = ItemStats()
        
        for item in self.equipped.values():
            if item:
                for stat_name, value in item.stats.__dict__.items():
                    current = getattr(total, stat_name)
                    setattr(total, stat_name, current + value)
        
        for ring in self.rings:
            if ring:
                for stat_name, value in ring.stats.__dict__.items():
                    current = getattr(total, stat_name)
                    setattr(total, stat_name, current + value)
        
        return total

class Player(Entity):
    def __init__(self, x: int = 0, y: int = 0):
        super().__init__("Player", EntityType.PLAYER, level=1)
        self.x = x
        self.y = y
        self.speed = 1
        self.inventory = Inventory()
        self.base_stats = Stats(
            strength=10, defence=5, health=20, speed=5, stamina=15,
            dexterity=5, magic_power=5, magic_defence=5, wisdom=5, intelligence=5
        )
        self.initialize_stats()
        self.experience = 0
        self.next_level_exp = 100
        self.skill_points = 0
        self.unlocked_skills = []

    def get_total_stats(self) -> Stats:
        equipment_stats = self.inventory.get_total_stats()
        total_stats = Stats()
        
        for stat_name in self.current_stats.__dict__:
            base = getattr(self.current_stats, stat_name)
            bonus = getattr(equipment_stats, stat_name)
            setattr(total_stats, stat_name, base + bonus)
            
        return total_stats

    def move(self, dx: int, dy: int):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def gain_experience(self, amount: int):
        self.experience += amount
        if self.experience >= self.next_level_exp:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        self.points_available = 2
        self.skill_points += 2
        self.experience -= self.next_level_exp
        self.next_level_exp = int(self.next_level_exp * 1.3)
        self.initialize_stats()