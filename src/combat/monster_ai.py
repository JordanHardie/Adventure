# combat/monster_ai.py

from enum import Enum, auto
from typing import Dict, List
from ..engine.generics import RandomUtils

class BehaviorType(Enum):
    AGGRESSIVE = auto()  # Prefers direct damage
    DEFENSIVE = auto()   # Prioritizes buffing/healing when low HP
    RANGED = auto()      # Tries to use magic/ranged attacks
    TRICKSTER = auto()   # Alternates between debuffs and attacks
    AMBUSHER = auto()    # Builds up for strong attacks
    BOSS = auto()        # Uses all abilities strategically

class MonsterAI:
    def __init__(self, monster, behavior: str, actions: Dict):
        self.monster = monster
        self.behavior = BehaviorType[behavior.upper()]
        self.actions = actions
        self.last_action = None
        self.turns_since_buff = 0

    def choose_action(self, player) -> dict:
        """Choose the next action based on behavior type and current state"""
        
        # Get viable actions based on behavior and state
        viable_actions = self._get_viable_actions(player)
        
        # Calculate weights based on current situation
        weights = []
        for action_name in viable_actions:
            base_weight = self.actions[action_name]["weight"]
            situational_weight = self._calculate_situational_weight(action_name, player)
            weights.append(base_weight * situational_weight)

        # Choose action based on weights
        chosen_action_name = RandomUtils.choices(viable_actions, weights=weights)[0]
        chosen_action = self.actions[chosen_action_name]
        
        # Update state
        self.last_action = chosen_action_name
        if chosen_action["type"] in ["buff", "heal"]:
            self.turns_since_buff = 0
        else:
            self.turns_since_buff += 1

        # Get random message for the action
        message = RandomUtils.choice(chosen_action["messages"])
        
        return {
            "name": chosen_action_name,
            "action": chosen_action,
            "message": message.format(name=self.monster.name, target=player.name)
        }

    def _get_viable_actions(self, player) -> List[str]:
        """Get list of viable actions based on current state"""
        viable = []
        hp_percent = self.monster.current_hp / self.monster.max_hp

        for name, action in self.actions.items():
            # Skip healing if at full health
            if action["type"] == "heal" and hp_percent > 0.9:
                continue
                
            # Skip buffs if recently buffed
            if action["type"] == "buff" and self.turns_since_buff < 3:
                continue

            viable.append(name)

        return viable if viable else list(self.actions.keys())

    def _calculate_situational_weight(self, action_name: str, player) -> float:
        """Calculate situational weight multiplier for an action"""
        action = self.actions[action_name]
        action_type = action["type"]
        hp_percent = self.monster.current_hp / self.monster.max_hp
        weight_mult = 1.0

        match self.behavior:
            case BehaviorType.AGGRESSIVE:
                if action_type in ["physical", "magic"]:
                    weight_mult = 1.5
                elif hp_percent < 0.3 and action_type == "heal":
                    weight_mult = 2.0

            case BehaviorType.DEFENSIVE:
                if hp_percent < 0.5 and action_type in ["heal", "buff"]:
                    weight_mult = 2.0
                elif hp_percent > 0.8 and action_type in ["physical", "magic"]:
                    weight_mult = 1.3

            case BehaviorType.RANGED:
                if action_type == "magic":
                    weight_mult = 1.5
                elif hp_percent < 0.4:
                    weight_mult = 0.7

            case BehaviorType.TRICKSTER:
                if self.last_action:
                    # Prefer alternating between attacks and debuffs
                    if self.last_action["type"] == "debuff" and action_type in ["physical", "magic"]:
                        weight_mult = 1.5
                    elif self.last_action["type"] in ["physical", "magic"] and action_type == "debuff":
                        weight_mult = 1.5

            case BehaviorType.AMBUSHER:
                if not self.last_action:
                    # First turn, prefer buffs/preparation
                    if action_type in ["buff", "special"]:
                        weight_mult = 2.0
                elif self.last_action["type"] in ["buff", "special"]:
                    # Follow up with strong attack
                    if action_type in ["physical", "magic"]:
                        weight_mult = 2.0

            case BehaviorType.BOSS:
                if hp_percent < 0.3:
                    # Desperate times
                    if action_type in ["special", "magic"]:
                        weight_mult = 2.0
                elif self.turns_since_buff > 4:
                    # Haven't buffed in a while
                    if action_type == "buff":
                        weight_mult = 1.5

        return weight_mult