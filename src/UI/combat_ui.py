import pygame
from ..combat.entity import Entity
from ..engine.generics import BaseUI
from ..config.game_config import GameConfig

class CombatUI(BaseUI):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 32)
        self.large_font = pygame.font.SysFont(None, 48)
        self.selected_action = 0
        self.actions = ["Attack", "Magic", "Item", "Run"]
        self.combat_log = []
        self.max_log_lines = 3
        self.visible = True  # Make sure UI is visible by default

    def add_to_log(self, message: str):
        self.combat_log.append(message)
        if len(self.combat_log) > self.max_log_lines:
            self.combat_log.pop(0)

    def draw_entity_stats(self, entity: Entity, x: int, y: int):
        hp_text = f"HP: {entity.current_hp}/{entity.max_hp}"
        level_text = f"Lv.{entity.level} {entity.name}"
        hp_surface = self.font.render(hp_text, True, GameConfig.WHITE)
        level_surface = self.font.render(level_text, True, GameConfig.WHITE)
        self.screen.blit(level_surface, (x, y))
        self.screen.blit(hp_surface, (x, y + 30))

    def draw_combat_log(self):
        log_y = self.screen.get_height() // 2 - 50
        for i, message in enumerate(self.combat_log):
            text = self.font.render(message, True, GameConfig.WHITE)
            x = (self.screen.get_width() - text.get_width()) // 2
            self.screen.blit(text, (x, log_y + i * 30))

    def draw_combat_menu(self):
        menu_y = self.screen.get_height() - 150
        for i, action in enumerate(self.actions):
            color = GameConfig.WHITE if i == self.selected_action else (150, 150, 150)
            text = self.font.render(action, True, color)
            self.screen.blit(text, (50 + i * 200, menu_y))

    def draw_combat_scene(self, player: Entity, enemy: Entity):
        self.screen.fill(GameConfig.BLACK)

        # Draw enemy stats at the top
        enemy_text = self.large_font.render(enemy.name, True, GameConfig.WHITE)
        enemy_x = (self.screen.get_width() - enemy_text.get_width()) // 2
        self.screen.blit(enemy_text, (enemy_x, 100))
        self.draw_entity_stats(enemy, enemy_x, 150)

        # Draw player stats at the bottom
        self.draw_entity_stats(player, 50, self.screen.get_height() - 200)

        # Draw combat log in the middle
        self.draw_combat_log()

        # Draw combat menu at the bottom
        self.draw_combat_menu()

        pygame.display.flip()

    def render(self, player, enemy):
        if not self.visible:
            return
        self.draw_combat_scene(player, enemy)

    def handle_input(self) -> str:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_action = (self.selected_action - 1) % len(self.actions)
                elif event.key == pygame.K_RIGHT:
                    self.selected_action = (self.selected_action + 1) % len(self.actions)
                elif event.key == pygame.K_RETURN:
                    return self.actions[self.selected_action].lower()
        return None