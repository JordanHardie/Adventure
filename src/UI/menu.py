import pygame
from ..engine.generics import BaseUI
from ..config.game_config import GameConfig
from ..engine.generics import save_game_data, load_game_data

class Menu(BaseUI):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.SysFont(None, 74)
        self.small_font = pygame.font.SysFont(None, 54)
        self.title = self.font.render("Adventure!", True, GameConfig.WHITE)
        self.new_game = self.small_font.render("New Game", True, GameConfig.WHITE)
        self.continue_game = self.small_font.render("Continue Game", True, GameConfig.WHITE)
        self.selected = 0
        self.visible = True

    def has_save(self):
        return load_game_data() is not None

    def save_game(self, player_x, player_y):
        save_game_data({'x': player_x, 'y': player_y})

    def load_game(self):
        data = load_game_data()
        return data.get('x', 0), data.get('y', 0) if data else (0, 0)

    def render(self):
        if not self.visible:
            return
            
        self.screen.fill(GameConfig.BLACK)
        
        # Render title
        title_rect = self.title.get_rect(centerx=self.screen.get_width()//2, y=100)
        self.screen.blit(self.title, title_rect)
        
        # Render menu options
        new_game_color = GameConfig.WHITE if self.selected == 0 else (150, 150, 150)
        continue_color = GameConfig.WHITE if self.selected == 1 else (150, 150, 150)
        
        new_game = self.small_font.render("New Game", True, new_game_color)
        new_game_rect = new_game.get_rect(centerx=self.screen.get_width()//2, y=300)
        self.screen.blit(new_game, new_game_rect)
        
        if self.has_save():
            continue_game = self.small_font.render("Continue Game", True, continue_color)
            continue_rect = continue_game.get_rect(centerx=self.screen.get_width()//2, y=400)
            self.screen.blit(continue_game, continue_rect)
        
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