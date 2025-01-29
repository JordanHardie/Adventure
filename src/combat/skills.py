from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional

class SkillType(Enum):
    PHYSICAL = auto()
    MAGICAL = auto()
    SUPPORT = auto()
    PASSIVE = auto()

class BuffType(Enum):
    STRENGTH = auto()
    DEFENCE = auto()
    MAGIC_POWER = auto()
    MAGIC_DEFENCE = auto()
    SPEED = auto()
    DEXTERITY = auto()
    HEALTH_REGEN = auto()
    MANA_REGEN = auto()

class DebuffType(Enum):
    WEAKNESS = auto()     # Reduced strength
    VULNERABLE = auto()   # Reduced defence
    SLOW = auto()        # Reduced speed
    CONFUSION = auto()   # Reduced accuracy/dexterity
    BURNING = auto()     # DoT
    POISONED = auto()    # DoT
    FROZEN = auto()      # Can't move
    STUNNED = auto()     # Skip turn

@dataclass
class SkillRequirement:
    strength: int = 0
    defence: int = 0
    magic_power: int = 0
    magic_defence: int = 0
    speed: int = 0
    dexterity: int = 0
    wisdom: int = 0
    intelligence: int = 0
    level: int = 1

@dataclass
class Buff:
    type: BuffType
    magnitude: float
    duration: int
    source: str

@dataclass
class Debuff:
    type: DebuffType
    magnitude: float
    duration: int
    source: str

@dataclass
class Skill:
    name: str
    description: str
    skill_type: SkillType
    requirements: SkillRequirement
    mana_cost: int
    stamina_cost: int
    cooldown: int
    current_cooldown: int = 0
    unlocked: bool = False
    
    # For active skills
    base_damage: int = 0
    scaling: Dict[str, float] = None  # stat name -> scaling factor
    buff: Optional[Buff] = None
    debuff: Optional[Debuff] = None
    
    # For passive skills
    passive_buffs: List[Buff] = None

    def meets_requirements(self, player) -> bool:
        """Check if player meets skill requirements"""
        if player.level < self.requirements.level:
            return False
            
        for stat, required in self.requirements.__dict__.items():
            if getattr(player.current_stats, stat, 0) < required:
                return False
                
        return True

    def is_available(self) -> bool:
        """Check if skill is ready to use"""
        return self.unlocked and self.current_cooldown == 0

    def update_cooldown(self):
        """Update skill cooldown"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1