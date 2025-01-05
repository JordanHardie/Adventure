import random
import pygame

# World components
from ..world.world import World
from ..engine.player import Player

# UI components
from ..UI.menu import Menu
from ..UI.combat_ui import CombatUI
from ..UI.level_up_ui import LevelUpUI
from ..UI.inventory_ui import InventoryUI
from ..UI.combat_log_ui import CombatLogUI

# Configuration
from ..config.game_config import GameConfig
from ..config.font_config import FontConfig
from ..engine.generics import save_game_data, load_game_data

# Combat system
from ..combat.combat_manager import CombatManager
from ..combat.encounter_manager import EncounterManager

class GameEngine:
    """
    Core game engine managing game state, rendering, and user input.
    Coordinates between world, UI, and combat systems.
    """
    
    def __init__(self):
        """Initialize game engine and all subsystems."""
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Adventure")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts and configs
        self.fonts = self._initialize_fonts()
        self.font_config = FontConfig(self.fonts)

        # Initialize world and player
        self.world = World(self)
        self.player = None

        # Initialize UI components
        self._initialize_ui()
        
        # Initialize combat system
        self.combat_manager = CombatManager()
        self.encounter_manager = EncounterManager()
        
        # Game state
        self.current_enemy = None
        self.fullscreen = True
        self.game_state = "menu"  # States: "menu", "game", "combat", "level_up"

    def _initialize_fonts(self):
        """Set up game fonts with fallback to default."""
        fonts = {}
        for font_name in GameConfig.FONTS:
            fonts[font_name] = pygame.font.SysFont(font_name, GameConfig.GRID_SIZE)
        if not fonts:
            fonts["default"] = pygame.font.SysFont(None, GameConfig.GRID_SIZE)
        return fonts

    def _initialize_ui(self):
        """Initialize all UI components."""
        self.menu = Menu(self.screen)
        self.combat_ui = CombatUI(self.screen)
        self.inventory_ui = InventoryUI(self.screen)
        self.level_up_ui = LevelUpUI(self.screen, pygame.font.SysFont(None, 32))
        self.combat_log = CombatLogUI(self.screen, pygame.font.SysFont(None, 24))

    def new_game(self):
        """Start a new game with fresh player state."""
        self.player = Player()
        self.game_state = "game"

    def continue_game(self):
        """Load saved game state."""
        save_data = load_game_data()
        if save_data:
            x, y = save_data.get('x', 0), save_data.get('y', 0)
            self.player = Player(x, y)
            self.game_state = "game"

    def handle_input(self) -> bool:
        """
        Route input handling based on game state.
        Returns: False if game should exit, True otherwise.
        """
        if self.game_state == "menu":
            return self._handle_menu_input()
        elif self.game_state == "combat":
            self.combat_log.visible = False
            return self._handle_combat_input()
        elif self.game_state == "level_up":
            return self._handle_level_up_input()
        return self._handle_game_input()

    def _handle_level_up_input(self) -> bool:
        """Handle input during level up screen."""
        if self.level_up_ui.handle_input(self.player):
            self.game_state = "game"
        return True

    def _handle_menu_input(self) -> bool:
        """Handle menu navigation and selection."""
        result = self.menu.handle_input()
        if result == "new":
            self.new_game()
        elif result == "continue":
            self.continue_game()
        return result is not None

    def _handle_combat_input(self) -> bool:
        """
        Process combat actions and their results.
        Returns: False if game should exit, True otherwise.
        """
        action = self.combat_ui.handle_input()
        if action == "quit":
            return False
        elif action == "run":
            self._end_combat("Got away safely!")
            return True
        elif action in ["attack", "magic", "item"]:
            return self._process_combat_action(action)
        return True

    def _process_combat_action(self, action: str) -> bool:
        """Process a single combat action and its results."""
        result = self.combat_manager.process_turn(self.player, self.current_enemy, action)
        self.combat_ui.add_to_log(result["message"])

        if self.current_enemy.current_hp <= 0:
            return self._handle_enemy_defeat()
        elif self.player.current_hp <= 0:
            self.combat_ui.add_to_log("You were defeated!")
            self.game_state = "menu"
            
        return True

    def _handle_enemy_defeat(self) -> bool:
        """Handle enemy defeat, experience gain, and potential level up."""
        exp_gain = self.current_enemy.level * 10
        exp_gain_bonus = exp_gain + self.current_enemy.level + self.current_enemy.meta_level
        exp_gain = exp_gain_bonus + self.current_enemy.level * (2 + random.randint(0, 3))
        self.combat_ui.add_to_log(f"Gained {exp_gain} experience!")
        self.combat_log.add_message(f"Defeated {self.current_enemy.name}! +{exp_gain} exp")
        
        leveled_up = self.player.gain_experience(exp_gain)
        if leveled_up:
            self.level_up_ui.show(5)  # Give 5 stat points on level up
            self.game_state = "level_up"
        else:
            self.game_state = "game"
            
        self.combat_log.visible = True
        return True

    def _end_combat(self, message: str):
        """Clean up combat state and display message."""
        self.combat_ui.add_to_log(message)
        self.game_state = "game"

    def _handle_game_input(self) -> bool:
        """
        Handle world exploration input and movement.
        Returns: False if game should exit, True otherwise.
        """
        if not self._handle_system_events():
            return False

        if self._handle_movement():
            self._check_encounters()

        return True

    def _handle_system_events(self) -> bool:
        """Handle system-level events like quit and fullscreen toggle."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game_data({'x': self.player.x, 'y': self.player.y})
                    self.game_state = "menu"
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_i:
                    self.inventory_ui.toggle()
                elif event.key == pygame.K_LSHIFT:
                    self.player.speed = 2
            elif event.type == pygame.KEYUP and event.key == pygame.K_LSHIFT:
                self.player.speed = 1
        return True

    def _handle_movement(self) -> bool:
        """Process player movement input. Returns True if player moved."""
        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y

        if keys[pygame.K_w]: self.player.move(0, -1)
        if keys[pygame.K_s]: self.player.move(0, 1)
        if keys[pygame.K_a]: self.player.move(-1, 0)
        if keys[pygame.K_d]: self.player.move(1, 0)

        return old_x != self.player.x or old_y != self.player.y

    def _check_encounters(self):
        """Check for and initiate random encounters."""
        coords = (self.player.x, self.player.y)
        chunk = self.world.get_chunk(
            coords[0] // self.world.chunk_size,
            coords[1] // self.world.chunk_size
        )
        local_x, local_y = (
            coords[0] % self.world.chunk_size,
            coords[1] % self.world.chunk_size,
        )
        biome = chunk.get_biome(local_x, local_y)

        should_encounter, monster_name = self.encounter_manager.should_encounter(
            coords, biome
        )
        if should_encounter and monster_name:
            self.current_enemy = self.encounter_manager.generate_encounter(
                coords, biome
            )
            self.combat_manager.start_combat(self.player, self.current_enemy)
            self.game_state = "combat"

    def toggle_fullscreen(self):
        """Toggle between fullscreen and windowed mode."""
        self.fullscreen = not self.fullscreen
        mode = (
            pygame.FULLSCREEN if self.fullscreen
            else (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        )
        self.screen = pygame.display.set_mode(
            (0, 0) if self.fullscreen else mode
        )

    def render(self):
        """Render the current game state."""
        if self.game_state == "menu":
            self.menu.render()
        elif self.game_state == "combat":
            self.combat_ui.draw_combat_scene(self.player, self.current_enemy)
        else:
            self._render_game_world()
            
        pygame.display.flip()

    def _render_game_world(self):
        """Render the game world, player, and UI overlays."""
        self.screen.fill(GameConfig.BLACK)
        
        screen_width, screen_height = self.screen.get_size()
        half_width = screen_width // (2 * GameConfig.GRID_SIZE)
        half_height = screen_height // (2 * GameConfig.GRID_SIZE)
        
        self._render_world(half_width, half_height)
        self._render_player(screen_width, screen_height)
        self.inventory_ui.render(self.player)
        self.combat_log.draw()
        
        if self.game_state == "level_up":
            self.level_up_ui.draw(self.player.current_stats)

    def _render_world(self, half_width: int, half_height: int):
        """Render the visible world tiles around the player."""
        px, py = self.player.x, self.player.y
        for y in range(-half_height, half_height + 1):
            for x in range(-half_width, half_width + 1):
                wx, wy = px + x, py + y
                chunk = self.world.get_chunk(
                    wx // self.world.chunk_size,
                    wy // self.world.chunk_size
                )
                local_x, local_y = (
                    wx % self.world.chunk_size,
                    wy % self.world.chunk_size,
                )
                char, color = chunk.terrain[local_y][local_x]
                font_name = chunk.fonts[local_y][local_x]
                text = self.fonts[font_name].render(char, True, color)
                screen_x = (x + half_width) * GameConfig.GRID_SIZE
                screen_y = (y + half_height) * GameConfig.GRID_SIZE
                self.screen.blit(text, (screen_x, screen_y))

    def _render_player(self, screen_width: int, screen_height: int):
        """Render the player character at the center of the screen."""
        player_font = next(iter(self.fonts.values()))
        player_text = player_font.render(
            GameConfig.PLAYER_SYMBOL, True, GameConfig.WHITE
        )
        player_x = screen_width // 2 - GameConfig.GRID_SIZE // 2
        player_y = screen_height // 2 - GameConfig.GRID_SIZE // 2
        self.screen.blit(player_text, (player_x, player_y))

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.render()
            self.clock.tick(GameConfig.FPS)
        pygame.quit()