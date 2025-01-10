import pygame
from typing import Optional, Tuple
from ..combat.skill_tree import SkillTree, SkillTreeNode, SkillBranch
from ..config.game_config import GameConfig
from ..engine.generics import BaseUI

class SkillTreeUI(BaseUI):
    def __init__(self, screen):
        super().__init__(screen)
        self.selected_branch = SkillBranch.WARRIOR
        self.selected_node: Optional[SkillTreeNode] = None
        self.font = pygame.font.SysFont(None, 32)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Colors
        self.colors = {
            "background": (20, 20, 30),
            "node_unlocked": (0, 255, 0),
            "node_available": (255, 255, 0),
            "node_locked": (150, 150, 150),
            "node_selected": (255, 165, 0),
            "line": (100, 100, 100),
            "text": GameConfig.WHITE,
            "branch_selected": (255, 165, 0),
            "branch_unselected": (150, 150, 150)
        }
        
        # Layout
        self.node_radius = 20
        self.node_spacing = 100
        self.branch_height = 40
        self.margin = 50
        self.tree_start_x = 200  # Space for branch selection
        
        self._init_branch_buttons()

    def _init_branch_buttons(self):
        """Initialize branch selection buttons"""
        self.branch_buttons = {}
        y = self.margin
        
        for branch in SkillBranch:
            rect = pygame.Rect(
                20, y, 
                150, self.branch_height
            )
            self.branch_buttons[branch] = rect
            y += self.branch_height + 10

    def _draw_node(self, node: SkillTreeNode, skill_tree: SkillTree, player):
        """Draw a single skill node"""
        # Calculate screen position
        x = self.tree_start_x + node.position[0] * self.node_spacing + self.margin
        y = node.position[1] * self.node_spacing + self.margin
        
        # Draw connections to parent nodes
        for parent in node.parents:
            parent_x = self.tree_start_x + parent.position[0] * self.node_spacing + self.margin
            parent_y = parent.position[1] * self.node_spacing + self.margin
            pygame.draw.line(self.screen, self.colors["line"], 
                           (parent_x, parent_y), (x, y), 2)

        # Determine node color
        if node.skill.unlocked:
            color = self.colors["node_unlocked"]
        elif skill_tree.can_unlock_skill(node, player):
            color = self.colors["node_available"]
        else:
            color = self.colors["node_locked"]
            
        if node == self.selected_node:
            color = self.colors["node_selected"]

        # Draw node
        pygame.draw.circle(self.screen, color, (x, y), self.node_radius)
        
        # Draw skill name
        text = self.small_font.render(node.skill.name, True, self.colors["text"])
        text_rect = text.get_rect(center=(x, y + self.node_radius + 10))
        self.screen.blit(text, text_rect)

        return pygame.Rect(x - self.node_radius, y - self.node_radius, 
                         self.node_radius * 2, self.node_radius * 2)

    def _draw_skill_info(self, node: SkillTreeNode, skill_tree: SkillTree, player):
        """Draw detailed information about selected skill"""
        if not node:
            return

        info_x = self.screen.get_width() - 300
        info_y = self.margin
        line_height = 25

        # Draw skill name
        name_text = self.font.render(node.skill.name, True, self.colors["text"])
        self.screen.blit(name_text, (info_x, info_y))
        info_y += line_height * 2

        # Draw description
        desc_text = self.small_font.render(node.skill.description, True, self.colors["text"])
        self.screen.blit(desc_text, (info_x, info_y))
        info_y += line_height * 2

        # Draw requirements
        reqs = node.skill.requirements.__dict__
        req_text = self.small_font.render("Requirements:", True, self.colors["text"])
        self.screen.blit(req_text, (info_x, info_y))
        info_y += line_height

        for stat, value in reqs.items():
            if value > 0:
                current = getattr(player.current_stats, stat, 0)
                color = (0, 255, 0) if current >= value else (255, 0, 0)
                text = self.small_font.render(
                    f"{stat.capitalize()}: {value}", True, color
                )
                self.screen.blit(text, (info_x + 20, info_y))
                info_y += line_height

        # Draw costs
        info_y += line_height
        if node.skill.mana_cost > 0:
            mana_text = self.small_font.render(
                f"Mana Cost: {node.skill.mana_cost}", True, self.colors["text"]
            )
            self.screen.blit(mana_text, (info_x, info_y))
            info_y += line_height

        if node.skill.stamina_cost > 0:
            stamina_text = self.small_font.render(
                f"Stamina Cost: {node.skill.stamina_cost}", True, self.colors["text"]
            )
            self.screen.blit(stamina_text, (info_x, info_y))
            info_y += line_height

        # Draw unlock button if available
        if not node.skill.unlocked and skill_tree.can_unlock_skill(node, player):
            button_rect = pygame.Rect(info_x, info_y + 20, 150, 40)
            pygame.draw.rect(self.screen, (0, 255, 0), button_rect)
            unlock_text = self.small_font.render("Unlock Skill", True, (0, 0, 0))
            text_rect = unlock_text.get_rect(center=button_rect.center)
            self.screen.blit(unlock_text, text_rect)

    def handle_click(self, pos: Tuple[int, int], skill_tree: SkillTree, player) -> bool:
        """Handle mouse clicks"""
        if not self.visible:
            return False

        # Check branch buttons
        for branch, rect in self.branch_buttons.items():
            if rect.collidepoint(pos):
                self.selected_branch = branch
                self.selected_node = None
                return True

        # Check skill nodes
        nodes = skill_tree.branches[self.selected_branch]
        for node in nodes:
            node_pos = (
                self.tree_start_x + node.position[0] * self.node_spacing + self.margin,
                node.position[1] * self.node_spacing + self.margin
            )
            node_rect = pygame.Rect(
                node_pos[0] - self.node_radius,
                node_pos[1] - self.node_radius,
                self.node_radius * 2,
                self.node_radius * 2
            )
            if node_rect.collidepoint(pos):
                self.selected_node = node
                return True

        # Check unlock button
        if self.selected_node and not self.selected_node.skill.unlocked:
            info_x = self.screen.get_width() - 300
            button_rect = pygame.Rect(info_x, 500, 150, 40)  # Approximate position
            if button_rect.collidepoint(pos) and skill_tree.can_unlock_skill(self.selected_node, player):
                skill_tree.unlock_skill(self.selected_node, player)
                return True

        return False

    def render(self, skill_tree: SkillTree, player):
        """Render the skill tree UI"""
        if not self.visible:
            return

        # Draw background
        self.screen.fill(self.colors["background"])

        # Draw branch selection
        for branch, rect in self.branch_buttons.items():
            color = self.colors["branch_selected"] if branch == self.selected_branch else self.colors["branch_unselected"]
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(branch.value, True, self.colors["text"])