from ..config.game_config import GameConfig

class CombatLogUI:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.messages = []
        self.max_messages = 5
        self.visible = True

    def add_message(self, message):
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)

    def draw(self):
        if not self.visible:
            return
            
        y_offset = self.screen.get_height() - (self.max_messages * 25 + 10)
        for i, message in enumerate(self.messages):
            text = self.font.render(message, True, GameConfig.WHITE)
            self.screen.blit(text, (10, y_offset + i * 25))