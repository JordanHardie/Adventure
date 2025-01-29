"""
Main game engine module, responsible for initializing and coordinating game systems.
"""
from ..world.world import World

from .core.game_state import GameState
from .core.ui_manager import UIManager
from .core.input_manager import InputManager
from .core.system_manager import SystemManager
from .core.display_manager import DisplayManager
from .core.services import ConfigService, with_error_handling

class GameEngine:
    """
    Main game engine class that coordinates all game systems and manages the game loop.
    Handles initialization, updates, and cleanup of game components.
    """

    def __init__(self):
        """Initialize game engine and all core systems."""
        # Initialize configuration and logging
        self.config = ConfigService()
        self.logger = self.config.logger
        self.logger.info("Initializing game engine...")

        try:
            # Initialize core systems
            self.display_manager = self._init_display_manager()
            self.ui_manager = self._init_ui_manager()
            self.systems = self._init_system_manager()
            self.input_manager = InputManager()

            # Store reference to loaded fonts
            self.fonts = self.display_manager.fonts

            # Initialize world and game state
            self.world = self._init_world()
            self.state = self._init_game_state()

            self.logger.info("Game engine initialization complete")

        except Exception as e:
            self.logger.error(f"Error during game engine initialization: {str(e)}")
            raise

    @with_error_handling
    def _init_display_manager(self) -> DisplayManager:
        """Initialize the display manager."""
        self.logger.debug("Initializing display manager...")
        display_manager = DisplayManager()
        return display_manager

    @with_error_handling
    def _init_ui_manager(self) -> UIManager:
        """Initialize the UI manager."""
        self.logger.debug("Initializing UI manager...")
        self.ui_manager = UIManager(self.display_manager.screen)
        self.ui_manager.show_loading(0.4, "Loading systems...")
        return self.ui_manager

    @with_error_handling
    def _init_system_manager(self) -> SystemManager:
        """Initialize the system manager."""
        self.logger.debug("Initializing system manager...")
        return SystemManager()

    @with_error_handling
    def _init_world(self) -> World:
        """Initialize the game world."""
        self.logger.debug("Generating world...")
        self.ui_manager.show_loading(0.6, "Generating world...")
        return World(self)

    @with_error_handling
    def _init_game_state(self) -> GameState:
        """Initialize the game state."""
        self.logger.debug("Initializing game state...")
        self.ui_manager.show_loading(0.8, "Finalizing...")

        state = GameState(
            self.display_manager,
            self.ui_manager,
            self.systems
        )
        state.set_world(self.world)
        return state

    @with_error_handling
    def run(self):
        """Main game loop."""
        self.logger.info("Starting game loop")
        running = True

        try:
            while running:
                running = self.input_manager.handle_input(self.state)
                self.systems.update(self.state)
                self._render_frame()
                self.display_manager.clock.tick(self.config.get_config("game_config")["FPS"])

        except Exception as e:
            self.logger.error(f"Error in game loop: {str(e)}")
            raise

        finally:
            self.cleanup()

    @with_error_handling
    def _render_frame(self):
        """Render a single frame."""
        self.display_manager.render(
            self.state,
            self.world,
            self.state.player,
            self.ui_manager
        )

    @with_error_handling
    def cleanup(self):
        """Clean up resources before exit."""
        self.logger.info("Cleaning up game resources...")
        self.display_manager.cleanup()
        self.logger.info("Cleanup complete")