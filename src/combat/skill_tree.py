from enum import Enum
from typing import Dict, List, Optional
from .skills import Skill, SkillType, SkillRequirement

class SkillTreeNode:
    def __init__(self, skill: Skill, position: tuple[int, int]):
        self.skill = skill
        self.position = position  # (x, y) for UI placement
        self.children: List['SkillTreeNode'] = []
        self.parents: List['SkillTreeNode'] = []
        self.skill_points_required = 1

    def add_child(self, child: 'SkillTreeNode'):
        """Add a child node (skill that requires this one)"""
        self.children.append(child)
        child.parents.append(self)

class SkillBranch(Enum):
    WARRIOR = "Warrior"     # Physical damage and defense
    ASSASSIN = "Assassin"   # Speed and critical hits
    MAGE = "Mage"          # Magic damage and utility
    PALADIN = "Paladin"    # Hybrid physical/support
    RANGER = "Ranger"      # Ranged and traps
    MONK = "Monk"          # Martial arts and chi

class SkillTree:
    def __init__(self):
        self.branches: Dict[SkillBranch, List[SkillTreeNode]] = {
            branch: [] for branch in SkillBranch
        }
        self.available_points = 0
        self._initialize_trees()

    def _initialize_trees(self):
        """Initialize all skill trees with their nodes and connections"""
        self._init_warrior_tree()
        self._init_assassin_tree()
        self._init_mage_tree()
        self._init_paladin_tree()
        self._init_ranger_tree()
        self._init_monk_tree()

    def _init_warrior_tree(self):
        # Basic warrior skills
        slash = SkillTreeNode(
            Skill(
                name="Slash",
                description="A basic sword attack",
                skill_type=SkillType.PHYSICAL,
                requirements=SkillRequirement(strength=5),
                mana_cost=0,
                stamina_cost=10,
                cooldown=0,
                base_damage=15,
                scaling={"strength": 1.2}
            ),
            position=(0, 0)
        )

        heavy_strike = SkillTreeNode(
            Skill(
                name="Heavy Strike",
                description="A powerful overhead attack",
                skill_type=SkillType.PHYSICAL,
                requirements=SkillRequirement(strength=15, level=3),
                mana_cost=0,
                stamina_cost=25,
                cooldown=2,
                base_damage=30,
                scaling={"strength": 1.8}
            ),
            position=(0, 1)
        )

        # Connect nodes
        slash.add_child(heavy_strike)
        
        # Add to warrior branch
        self.branches[SkillBranch.WARRIOR].extend([slash, heavy_strike])

    def _init_mage_tree(self):
        # Basic mage skills
        fire_bolt = SkillTreeNode(
            Skill(
                name="Fire Bolt",
                description="A basic fire attack",
                skill_type=SkillType.MAGICAL,
                requirements=SkillRequirement(magic_power=5),
                mana_cost=10,
                stamina_cost=0,
                cooldown=0,
                base_damage=12,
                scaling={"magic_power": 1.5}
            ),
            position=(0, 0)
        )

        flame_burst = SkillTreeNode(
            Skill(
                name="Flame Burst",
                description="Area of effect fire damage",
                skill_type=SkillType.MAGICAL,
                requirements=SkillRequirement(magic_power=15, intelligence=10, level=3),
                mana_cost=25,
                stamina_cost=0,
                cooldown=3,
                base_damage=25,
                scaling={"magic_power": 2.0}
            ),
            position=(0, 1)
        )

        # Connect nodes
        fire_bolt.add_child(flame_burst)
        
        # Add to mage branch
        self.branches[SkillBranch.MAGE].extend([fire_bolt, flame_burst])

    def can_unlock_skill(self, node: SkillTreeNode, player) -> bool:
        """Check if a skill can be unlocked"""
        # Check if we have points available
        if self.available_points < node.skill_points_required:
            return False

        # Check if all parent skills are unlocked
        if not all(parent.skill.unlocked for parent in node.parents):
            return False

        # Check if player meets skill requirements
        return node.skill.meets_requirements(player)

    def unlock_skill(self, node: SkillTreeNode, player) -> bool:
        """Attempt to unlock a skill"""
        if not self.can_unlock_skill(node, player):
            return False

        self.available_points -= node.skill_points_required
        node.skill.unlocked = True
        return True

    def add_skill_points(self, points: int):
        """Add skill points to be spent"""
        self.available_points += points

    def get_available_skills(self, player) -> Dict[SkillBranch, List[SkillTreeNode]]:
        """Get all skills that can currently be unlocked"""
        available = {branch: [] for branch in SkillBranch}
        
        for branch, nodes in self.branches.items():
            for node in nodes:
                if not node.skill.unlocked and self.can_unlock_skill(node, player):
                    available[branch].append(node)
                    
        return available

    # Initialize other trees similarly
    def _init_assassin_tree(self):
        pass  # TODO: Implement assassin skills

    def _init_paladin_tree(self):
        pass  # TODO: Implement paladin skills

    def _init_ranger_tree(self):
        pass  # TODO: Implement ranger skills

    def _init_monk_tree(self):
        pass  # TODO: Implement monk skills