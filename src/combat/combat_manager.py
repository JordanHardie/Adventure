import random
from .entity import Entity, EntityType
from .loot_generator import LootGenerator

class CombatManager:
    def __init__(self):
        self.current_encounter = None
        self.turn_order = []
        self.loot_generator = LootGenerator()

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
                items, gold = self.loot_generator.generate_loot(defender.level, defender.meta_level)
                result["loot"] = {"items": items, "gold": gold}

        return result