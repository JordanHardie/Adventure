from .monster_ai import MonsterAI
from .entity import Entity, EntityType
from .loot_generator import LootGenerator
from ..engine.generics import RandomUtils, load_json_config

class CombatManager:
    def __init__(self):
        self.current_encounter = None
        self.turn_order = []
        self.loot_generator = LootGenerator()
        self.monster_data = load_json_config("monsters.json")["monsters"]
        self.monster_ai = None

    def start_combat(self, player: Entity, enemy: Entity):
        print("\n=== Starting Combat ===")
        print(f"Player - HP: {player.current_hp}/{player.max_hp}")
        print(f"Enemy - HP: {enemy.current_hp}/{enemy.max_hp}")
        try:
            self.current_encounter = (player, enemy)
            self.determine_turn_order()
            monster_config = self.monster_data[enemy.name]
            self.monster_ai = MonsterAI(enemy, monster_config["behavior"], monster_config["actions"])
            print(f"Turn order: {[e.name for e in self.turn_order]}")
        except Exception as e:
            print(f"ERROR starting combat: {str(e)}")
            raise

    def process_turn(self, attacker: Entity, defender: Entity, action: str) -> dict:
        result = {
            "damage_dealt": 0,
            "is_critical": False,
            "status_effects": [],
            "message": "",
            "loot": None
        }

        if attacker.entity_type == EntityType.PLAYER:
            self._process_player_action(attacker, defender, action, result)
        else:
            self._process_monster_action(attacker, defender, result)

        if defender.current_hp <= 0 and defender.entity_type == EntityType.MONSTER:
            items, gold = self.loot_generator.generate_loot(defender.level, defender.meta_level)
            result["loot"] = {"items": items, "gold": gold}

        return result

    def _process_player_action(self, player: Entity, monster: Entity, action: str, result: dict):
        if action == "attack":
            damage = self.calculate_damage(player, monster)
            monster.current_hp -= damage
            result["damage_dealt"] = damage
            result["message"] = f"You attack for {damage} damage!"

    def _process_monster_action(self, monster: Entity, player: Entity, result: dict):
        # Get AI decision
        action_choice = self.monster_ai.choose_action(player)
        action_type = action_choice["action"]["type"]
        
        match action_type:
            case "physical" | "magic":
                damage = self.calculate_damage(
                    monster, player, 
                    is_magical=(action_type == "magic")
                )
                player.current_hp -= damage
                result["damage_dealt"] = damage
                result["message"] = action_choice["message"] + f" Deals {damage} damage!"
                
            case "heal":
                heal_amount = max(5, monster.current_stats.health)
                monster.current_hp = min(
                    monster.max_hp,
                    monster.current_hp + heal_amount
                )
                result["message"] = action_choice["message"] + f" Heals for {heal_amount}!"
                
            case "buff":
                # For now, just use the message
                result["message"] = action_choice["message"]
                
            case "debuff":
                # For now, just use the message
                result["message"] = action_choice["message"]
                
            case "special":
                # Handle special cases with message for now
                result["message"] = action_choice["message"]

    def determine_turn_order(self):
        player, monster = self.current_encounter
        self.turn_order = sorted(
            [player, monster], 
            key=lambda x: x.current_stats.speed, 
            reverse=True
        )

    def calculate_damage(self, attacker: Entity, defender: Entity, is_magical: bool = False) -> int:
        if is_magical:
            attack = attacker.current_stats.magic_power
            defence = defender.current_stats.magic_defence
        else:
            attack = attacker.current_stats.strength
            defence = defender.current_stats.defence

        base_damage = max(1, attack - defence // 2)
        crit_chance = attacker.current_stats.dexterity * 0.05
        is_crit = RandomUtils.chance(crit_chance)

        if is_crit:
            base_damage *= 2

        return base_damage