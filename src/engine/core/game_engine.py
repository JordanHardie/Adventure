from .game_state import GameState
from .display_manager import DisplayManager
from .input_manager import InputManager

class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.display = DisplayManager()
        self.input_handler = InputManager()
        self.world = World(self)
        self.player = None
        self.ui_manager = UIManager(self.display.screen)
        self.systems = SystemManager()

    def run(self):
        running = True
        while running:
            running = self.input_handler.handle_input(self.state)
            self.systems.update(self.state)
            self.display.render(self.state)
            self.display.clock.tick(GameConfig.FPS)