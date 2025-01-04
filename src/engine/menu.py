import os
import json
import pygame
from ..config.game_config import GameConfig

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 74)
        self.small_font = pygame.font.SysFont(None, 54)
        self.title = self.font.render("Adventure!", True, GameConfig.WHITE)
        self.new_game = self.small_font.render("New Game", True, GameConfig.WHITE)
        self.continue_game = self.small_font.render("Continue Game", True, GameConfig.WHITE)
        self.selected = 0
        self.save_path = os.path.join(os.getenv('APPDATA'), 'Adventure', 'save.json')

    def has_save(self):
        return os.path.exists(self.save_path)

    def save_game(self, player_x, player_y):
        save_dir = os.path.dirname(self.save_path)
        os.makedirs(save_dir, exist_ok=True)
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump({'x': player_x, 'y': player_y}, f)

    def load_game(self):
        if self.has_save():
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('x', 0), data.get('y', 0)
        return 0, 0

    def render(self):
        self.screen.fill(GameConfig.BLACK)

        # Center title
        title_x = (self.screen.get_width() - self.title.get_width()) // 2
        self.screen.blit(self.title, (title_x, 200))

        # Center buttons
        new_game_x = (self.screen.get_width() - self.new_game.get_width()) // 2
        continue_x = (self.screen.get_width() - self.continue_game.get_width()) // 2

        # Draw buttons with selection indicator
        if self.selected == 0:
            pygame.draw.rect(self.screen, GameConfig.WHITE,
                            (new_game_x - 10, 390, self.new_game.get_width() + 20, 50), 2)
        self.screen.blit(self.new_game, (new_game_x, 400))

        if self.has_save():
            if self.selected == 1:
                pygame.draw.rect(self.screen, GameConfig.WHITE,
                                (continue_x - 10, 490, self.continue_game.get_width() + 20, 50), 2)
            self.screen.blit(self.continue_game, (continue_x, 500))

        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    if self.has_save():
                        self.selected = (self.selected + 1) % 2
                if event.key == pygame.K_RETURN:
                    return "new" if self.selected == 0 else "continue"
        return "menu"
