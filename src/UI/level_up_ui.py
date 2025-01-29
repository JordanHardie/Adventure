import pygame
from ..engine.generics import BaseUI
from ..config.game_config import GameConfig

class LevelUpUI(BaseUI):
    def __init__(self, screen, font):
        super().__init__(screen)
        self.font = font
        self.points_available = 0
        self.selected_stat = 0
        self.stats = [
            "strength",
            "defence",
            "health",
            "speed",
            "stamina",
            "dexterity",
            "magic_power",
            "magic_defence",
            "wisdom",
            "intelligence",
        ]

    def show(self, points):
        self.points_available = points
        self.visible = True

    def hide(self):
        self.visible = False
        self.points_available = 0

    def draw(self, current_stats):
        if not self.visible:
            return

        # Draw semi-transparent background
        surface = pygame.Surface(self.screen.get_size())
        surface.fill(GameConfig.BLACK)
        surface.set_alpha(128)
        self.screen.blit(surface, (0, 0))

        # Draw level up menu
        title = self.font.render(
            f"Level Up! Points: {self.points_available}", True, GameConfig.WHITE
        )
        self.screen.blit(title, (400, 200))

        for i, stat in enumerate(self.stats):
            color = GameConfig.WHITE if i == self.selected_stat else (150, 150, 150)
            value = getattr(current_stats, stat)
            text = self.font.render(f"{stat.capitalize()}: {value}", True, color)
            self.screen.blit(text, (400, 250 + i * 30))

    def handle_input(self, player):
        for event in pygame.event.get(pygame.KEYDOWN):
            if event.key == pygame.K_UP:
                self.selected_stat = (self.selected_stat - 1) % len(self.stats)
            elif event.key == pygame.K_DOWN:
                self.selected_stat = (self.selected_stat + 1) % len(self.stats)
            elif event.key == pygame.K_RETURN and self.points_available > 0:
                stat_name = self.stats[self.selected_stat]
                current = getattr(player.base_stats, stat_name)
                setattr(player.base_stats, stat_name, current + 1)
                self.points_available -= 1
                player.initialize_stats()

                if self.points_available == 0:
                    self.hide()
                    return True
        return False

    def render(self, current_stats):
        if not self.visible:
            return

        # Draw semi-transparent background
        surface = pygame.Surface(self.screen.get_size())
        surface.fill(GameConfig.BLACK)
        surface.set_alpha(128)
        self.screen.blit(surface, (0, 0))

        # Draw level up menu
        title = self.font.render(f"Level Up!", True, GameConfig.WHITE)
        self.screen.blit(title, (400, 150))
    
        # Add skill points notification
        skill_text = self.font.render("2 Skill Points Added! (Press K to open skill tree)", True, GameConfig.WHITE)
        self.screen.blit(skill_text, (400, 180))

        points_text = self.font.render(f"Attribute Points: {self.points_available}", True, GameConfig.WHITE)
        self.screen.blit(points_text, (400, 220))

        for i, stat in enumerate(self.stats):
            color = GameConfig.WHITE if i == self.selected_stat else (150, 150, 150)
            value = getattr(current_stats, stat)
            text = self.font.render(f"{stat.capitalize()}: {value}", True, color)
            self.screen.blit(text, (400, 260 + i * 30))