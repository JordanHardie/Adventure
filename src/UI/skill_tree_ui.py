import pygame
from typing import Optional, Tuple
from ..engine.generics import BaseUI
from ..config.game_config import GameConfig
from ..combat.skill_tree import SkillTree, SkillTreeNode, SkillBranch

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
            "branch_unselected": (150, 150, 150),
            "exclusive_locked": (255, 0, 0, 128)  # Semi-transparent red for exclusive locked paths
        }

        # Layout
        self.node_radius = 20
        self.node_spacing = 100
        self.branch_height = 40
        self.margin = 50
        self.tree_start_x = 200  # Space for branch selection

        self.scroll_x = 0
        self.scroll_y = 0
        self.scroll_speed = 20  # Pixels per scroll tick

        # Viewport dimensions
        self.viewport_width = screen.get_width() - 600  # Leave space for UI elements
        self.viewport_height = screen.get_height() - 100  # Leave space for top/bottom margins
        self.viewport_x = (screen.get_width() - self.viewport_width) // 2
        self.viewport_y = 50   # Starting y position from top

        self._init_branch_buttons()

    def toggle(self):
        """Toggle visibility of the skill tree UI"""
        self.visible = not self.visible
        print(f"Toggling skill tree UI from {not self.visible} to {self.visible}")

    def _is_in_viewport(self, x: int, y: int) -> bool:
        """Check if a point is within the viewable area"""
        return (self.viewport_x <= x <= self.viewport_x + self.viewport_width and
                self.viewport_y <= y <= self.viewport_y + self.viewport_height)

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

    def handle_scroll(self, event, skill_tree: SkillTree):
        """Handle mouse wheel and keyboard scroll events"""
        if not self.visible:
            return

        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y += event.y * self.scroll_speed
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.scroll_x += self.scroll_speed
            elif event.key == pygame.K_RIGHT:
                self.scroll_x -= self.scroll_speed

        # Calculate max scroll bounds based on content
        branch_nodes = skill_tree.branches[self.selected_branch]
        if branch_nodes:
            max_y = max(node.position[1] * self.node_spacing + self.margin
                        for node in branch_nodes)
            max_x = max(node.position[0] * self.node_spacing + self.margin
                        for node in branch_nodes)
        else:
            max_y = max_x = 0

        # Constrain scrolling
        self.scroll_x = min(0, max(-max_x + self.viewport_width, self.scroll_x))
        self.scroll_y = min(0, max(-max_y + self.viewport_height, self.scroll_y))

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

    def _draw_node_connections(self, node: SkillTreeNode, skill_tree: SkillTree):
        """Draw connections between nodes with scroll offset"""
        base_x = self.viewport_x + self.scroll_x
        base_y = self.viewport_y + self.scroll_y

        x = base_x + node.position[0] * self.node_spacing
        y = base_y + node.position[1] * self.node_spacing

        for child in node.children:
            child_x = base_x + child.position[0] * self.node_spacing
            child_y = base_y + child.position[1] * self.node_spacing

            # Only draw if either endpoint is in viewport
            if self._is_in_viewport(x, y) or self._is_in_viewport(child_x, child_y):
                if child.exclusive_group:
                    if (child.exclusive_group in skill_tree.exclusive_groups and
                            skill_tree.exclusive_groups[child.exclusive_group] != child):
                        color = self.colors["exclusive_locked"]
                    else:
                        color = self.colors["line"]
                else:
                    color = self.colors["line"]

                pygame.draw.line(self.screen, color, (x, y), (child_x, child_y), 2)

    def _draw_skill_info(self, node: SkillTreeNode, skill_tree: SkillTree, player):
        """Draw detailed information about selected skill"""
        if not node:
            return

        # Place info panel on right side of screen, fixed position regardless of scroll
        info_x = self.viewport_x + self.viewport_width + 50  # Just past viewport
        info_y = self.viewport_y
        line_height = 25

        # Draw background panel
        panel_width = 280
        pygame.draw.rect(self.screen, (30, 30, 40),
                         (info_x - 10, info_y - 10, panel_width, self.viewport_height),
                         border_radius=5)

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

        # Draw cooldown if applicable
        if node.skill.cooldown > 0:
            cooldown_text = self.small_font.render(
                f"Cooldown: {node.skill.cooldown} turns", True, self.colors["text"]
            )
            self.screen.blit(cooldown_text, (info_x, info_y))
            info_y += line_height

        # Draw stat bonuses
        if node.stats_buff:
            info_y += line_height
            bonus_text = self.small_font.render("Stat Bonuses:", True, self.colors["text"])
            self.screen.blit(bonus_text, (info_x, info_y))
            info_y += line_height

            for stat, value in node.stats_buff.items():
                sign = '+' if value > 0 else ''
                text = self.small_font.render(
                    f"{stat.capitalize()}: {sign}{value}", True,
                    (0, 255, 0) if value > 0 else (255, 0, 0)
                )
                self.screen.blit(text, (info_x + 20, info_y))
                info_y += line_height

        # Draw exclusive group info if applicable
        if node.exclusive_group:
            info_y += line_height
            exclusive_text = self.small_font.render(
                f"Mutually exclusive with other", True, (255, 165, 0)
            )
            self.screen.blit(exclusive_text, (info_x, info_y))
            info_y += line_height
            group_text = self.small_font.render(
                f"{node.exclusive_group} skills", True, (255, 165, 0)
            )
            self.screen.blit(group_text, (info_x, info_y))
            info_y += line_height

        # Draw unlock button if available
        if not node.skill.unlocked and skill_tree.can_unlock_skill(node, player):
            button_rect = pygame.Rect(info_x, info_y + 20, panel_width - 20, 40)
            pygame.draw.rect(self.screen, (0, 255, 0), button_rect, border_radius=5)
            unlock_text = self.small_font.render("Unlock Skill", True, (0, 0, 0))
            text_rect = unlock_text.get_rect(center=button_rect.center)
            self.screen.blit(unlock_text, text_rect)

    def _draw_node_visuals(self, node: SkillTreeNode, skill_tree: SkillTree, player):
        """Draw node with scroll offset"""
        x = self.viewport_x + self.scroll_x + node.position[0] * self.node_spacing
        y = self.viewport_y + self.scroll_y + node.position[1] * self.node_spacing

        if not self._is_in_viewport(x, y):
            return

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
        if not self.visible:
            return

        print("\nRendering skill tree UI")
        print(f"Current branch: {self.selected_branch}")
        print(f"Available branches: {skill_tree.branches.keys()}")
        print(f"Nodes in current branch: {len(skill_tree.branches[self.selected_branch])}")

        # Draw semi-transparent background
        background = pygame.Surface(self.screen.get_size())
        background.fill(self.colors["background"])
        background.set_alpha(230)
        self.screen.blit(background, (0, 0))

        # Draw skill points available
        points_text = self.font.render(f"Skill Points: {skill_tree.available_points}", True, self.colors["text"])
        self.screen.blit(points_text, (20, 20))

        # Draw branch selection
        for branch, rect in self.branch_buttons.items():
            color = self.colors["branch_selected"] if branch == self.selected_branch else self.colors[
                "branch_unselected"]
            pygame.draw.rect(self.screen, color, rect)
            text = self.font.render(branch.value, True, self.colors["text"])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

        if self.selected_branch in skill_tree.branches:
            nodes = skill_tree.branches[self.selected_branch]

            # First pass - draw connections
            for node in nodes:
                self._draw_node_connections(node, skill_tree)

            # Second pass - draw nodes
            for node in nodes:
                self._draw_node_visuals(node, skill_tree, player)