from .core.game_state import GameState
from .core.ui_manager import UIManager
from .core.input_manager import InputManager
from .core.system_manager import SystemManager
from .core.display_manager import DisplayManager

from ..world.world import World
from ..config.game_config import GameConfig

class GameEngine:
    def __init__(self):
        self.display_manager = DisplayManager()
        self.ui_manager = UIManager(self.display_manager.screen)
        self.ui_manager.show_loading(0.4, "Loading systems...")
        
        self.systems = SystemManager()
        self.input_manager = InputManager()
        self.fonts = self.display_manager.fonts
        
        self.ui_manager.show_loading(0.6, "Generating world...")
        self.world = World(self)
        
        self.ui_manager.show_loading(0.8, "Finalizing...")
        self.state = GameState(self.display_manager, self.ui_manager, self.systems)
        self.state.set_world(self.world)
        
        # Initialize game state last since it needs references to other systems
        self.state = GameState(
            self.display_manager,
            self.ui_manager,
            self.systems
        )
        self.state.set_world(self.world)

    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.input_manager.handle_input(self.state)
            self.systems.update(self.state)
            self.display_manager.render(
                self.state, 
                self.world, 
                self.state.player, 
                self.ui_manager
            )
            self.display_manager.clock.tick(GameConfig.FPS)
            
        self.cleanup()

    def cleanup(self):
        """Clean up resources before exit"""
        self.display_manager.cleanup()