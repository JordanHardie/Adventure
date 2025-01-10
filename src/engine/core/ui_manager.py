import pygame

from ...UI.menu import Menu
from ...UI.combat_ui import CombatUI
from ...UI.level_up_ui import LevelUpUI
from ...UI.inventory_ui import InventoryUI
from ...UI.combat_log_ui import CombatLogUI
from ...UI.skill_tree_ui import SkillTreeUI
from ...UI.loading_screen import LoadingScreen

class UIManager:
    def __init__(self, screen):
        self.loading_screen = LoadingScreen(screen)
        
        self.loading_screen.update(0.2, "Initializing menus...")
        self.menu = Menu(screen)
        self.combat_ui = CombatUI(screen)
        self.skill_tree_ui = SkillTreeUI(screen)
        
        self.loading_screen.update(0.4, "Loading combat system...")
        self.level_up_ui = LevelUpUI(screen, pygame.font.SysFont(None, 32))
        self.combat_log = CombatLogUI(screen, pygame.font.SysFont(None, 24))
        
        self.loading_screen.update(0.6, "Loading inventory...")
        self.inventory_ui = InventoryUI(screen, combat_log=self.combat_log)
        
        self.loading_screen.update(1.0, "Ready!")

    def show_loading(self, progress: float, message: str):
        self.loading_screen.update(progress, message)

    def reset_ui_state(self):
        """Reset all UI components to their default state"""
        self.inventory_ui.hide()
        self.level_up_ui.hide()
        self.combat_log.visible = True

    def show_combat_ui(self):
        """Prepare UI for combat state"""
        self.combat_log.visible = False
        self.inventory_ui.hide()
        self.level_up_ui.hide()

    def show_game_ui(self):
        """Prepare UI for normal game state"""
        self.combat_log.visible = True
        self.inventory_ui.hide()
        self.level_up_ui.hide()