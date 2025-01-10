import pygame
from ..config.game_config import GameConfig

class LoadingScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 48)
        self._progress = 0
        self._message = ""

    def update(self, progress: float, message: str):
        self._progress = progress
        self._message = message
        self.render()
        pygame.display.flip()

    def render(self):
        self.screen.fill(GameConfig.BLACK)
        
        loading_text = self.font.render(self._message, True, GameConfig.WHITE)
        text_rect = loading_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(loading_text, text_rect)
        
        bar_width = 400
        bar_height = 20
        bar_x = (self.screen.get_width() - bar_width) // 2
        bar_y = text_rect.bottom + 20
        
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(self.screen, GameConfig.WHITE, 
                        (bar_x, bar_y, int(bar_width * self._progress), bar_height))