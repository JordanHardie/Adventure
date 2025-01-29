from enum import Enum
from typing import Dict, List, Optional
from .skills import Skill, SkillRequirement
from ..engine.generics import load_json_config

class SkillTreeNode:
    def __init__(self, skill: Skill, position: tuple[int, int], exclusive_group: Optional[str] = None):
        self.skill = skill
        self.position = position
        self.children: List['SkillTreeNode'] = []
        self.parents: List['SkillTreeNode'] = []
        self.exclusive_group = exclusive_group
        self.skill_points_required = 1
        self.stats_buff = {}

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
        self.exclusive_groups: Dict[str, SkillTreeNode] = {}
        self._load_skill_trees()

    def _load_skill_trees(self):
        """Load skill trees from JSON file"""
        try:
            print("Loading skill trees from JSON...")
            skill_trees = load_json_config("skill_trees.json")
            print(f"Loaded skill trees data: {list(skill_trees.keys())}")
            for branch_name, branch_data in skill_trees.items():
                print(f"Building branch: {branch_name}")
                branch = SkillBranch[branch_name]
                self._build_branch(branch, branch_data)
                print(f"Built branch {branch_name} with {len(self.branches[branch])} nodes")
        except Exception as e:
            print(f"Error loading skill trees: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def can_unlock_skill(self, node: SkillTreeNode, player) -> bool:
        """Check if a skill can be unlocked"""
        # Check if we have points available
        if self.available_points < node.skill_points_required:
            return False

        # Check if all parent skills are unlocked
        if not all(parent.skill.unlocked for parent in node.parents):
            return False

        # Check if player meets skill requirements
        if not node.skill.meets_requirements(player):
            return False

        # Check exclusive group
        if node.exclusive_group:
            if node.exclusive_group in self.exclusive_groups:
                chosen_node = self.exclusive_groups[node.exclusive_group]
                if chosen_node != node:
                    return False

        return True

    def unlock_skill(self, node: SkillTreeNode, player) -> bool:
        """Attempt to unlock a skill"""
        if not self.can_unlock_skill(node, player):
            return False

        self.available_points -= node.skill_points_required
        node.skill.unlocked = True

        # Handle exclusive group
        if node.exclusive_group:
            self.exclusive_groups[node.exclusive_group] = node

        # Apply stat buffs
        for stat, value in node.stats_buff.items():
            current = getattr(player.base_stats, stat)
            setattr(player.base_stats, stat, current + value)
        player.initialize_stats()

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

    def _build_branch(self, branch: SkillBranch, branch_data: dict):
        """Build a skill tree branch from JSON data"""
        nodes = {}  # Keep track of nodes by ID
        skills_data = branch_data["skills"]

        # First pass: Create all nodes
        for skill_id, skill_data in skills_data.items():
            # Create proper SkillRequirement object
            requirements = SkillRequirement(
                level=skill_data["requirements"].get("level", 1),
                strength=skill_data["requirements"].get("strength", 0),
                defence=skill_data["requirements"].get("defence", 0),
                magic_power=skill_data["requirements"].get("magic_power", 0),
                magic_defence=skill_data["requirements"].get("magic_defence", 0),
                speed=skill_data["requirements"].get("speed", 0),
                dexterity=skill_data["requirements"].get("dexterity", 0),
                wisdom=skill_data["requirements"].get("wisdom", 0),
                intelligence=skill_data["requirements"].get("intelligence", 0)
            )

            skill = Skill(
                name=skill_data["name"],
                description=skill_data["description"],
                skill_type=skill_data.get("type", "ACTIVE"),
                requirements=requirements,  # Now passing SkillRequirement object
                mana_cost=skill_data.get("mana_cost", 0),
                stamina_cost=skill_data.get("stamina_cost", 0),
                cooldown=skill_data.get("cooldown", 0),
                base_damage=skill_data.get("base_damage", 0),
                scaling=skill_data.get("scaling", {})
            )

            node = SkillTreeNode(
                skill=skill,
                position=tuple(skill_data["position"]),
                exclusive_group=skill_data.get("exclusive_group")
            )
            node.stats_buff = skill_data.get("stats", {})
            nodes[skill_id] = node
            self.branches[branch].append(node)

        # Second pass: Connect nodes
        for skill_id, skill_data in skills_data.items():
            if "children" in skill_data:
                parent_node = nodes[skill_id]
                for child_id in skill_data["children"]:
                    if child_id in nodes:
                        parent_node.add_child(nodes[child_id])