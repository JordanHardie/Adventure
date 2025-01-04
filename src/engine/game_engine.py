import pygame
from ..config.game_config import GameConfig
from ..config.font_config import FontConfig
from ..engine.player import Player
from ..world.world import World
from ..engine.menu import Menu
from ..combat.entity import EncounterManager, CombatManager
from ..combat.combat_ui import CombatUI

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        pygame.display.set_caption("Adventure")
        self.clock = pygame.time.Clock()
        self.fonts = self._initialize_fonts()
        self.font_config = FontConfig(self.fonts)
        self.menu = Menu(self.screen)
        self.combat_ui = CombatUI(self.screen)
        self.world = World(self)
        self.encounter_manager = EncounterManager()
        self.combat_manager = CombatManager()
        self.player = None
        self.current_enemy = None
        self.fullscreen = True
        self.game_state = "menu"  # "menu", "game", or "combat"

    def _initialize_fonts(self):
        fonts = {}
        for font_name in GameConfig.FONTS:
            fonts[font_name] = pygame.font.SysFont(font_name, GameConfig.GRID_SIZE)
        if not fonts:
            fonts["default"] = pygame.font.SysFont(None, GameConfig.GRID_SIZE)
        return fonts

    def new_game(self):
        self.player = Player()
        self.game_state = "game"

    def continue_game(self):
        x, y = self.menu.load_game()
        self.player = Player(x, y)
        self.game_state = "game"

    def handle_input(self) -> bool:
        if self.game_state == "menu":
            return self._handle_menu_input()
        elif self.game_state == "combat":
            return self._handle_combat_input()
        return self._handle_game_input()

    def _handle_menu_input(self) -> bool:
        result = self.menu.handle_input()
        if result == "new":
            self.new_game()
        elif result == "continue":
            self.continue_game()
        return result is not None

    def _handle_combat_input(self) -> bool:
        action = self.combat_ui.handle_input()
        if action == "quit":
            return False
        elif action == "run":
            self.combat_ui.add_to_log("Got away safely!")
            self.game_state = "game"
            return True
        elif action in ["attack", "magic", "item"]:
            result = self.combat_manager.process_turn(
                self.player, self.current_enemy, action
            )
            self.combat_ui.add_to_log(result["message"])

            if self.current_enemy.current_hp <= 0:
                exp_gain = self.current_enemy.level * 10
                self.combat_ui.add_to_log(f"Gained {exp_gain} experience!")
                self.player.gain_experience(exp_gain)
                self.game_state = "game"
            elif self.player.current_hp <= 0:
                self.combat_ui.add_to_log("You were defeated!")
                self.game_state = "menu"
        return True

    def _handle_game_input(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.menu.save_game(self.player.x, self.player.y)
                    self.game_state = "menu"
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_LSHIFT:
                    self.player.speed = 2
            elif event.type == pygame.KEYUP and event.key == pygame.K_LSHIFT:
                self.player.speed = 1

        keys = pygame.key.get_pressed()
        old_x, old_y = self.player.x, self.player.y

        if keys[pygame.K_w]:
            self.player.move(0, -1)
        if keys[pygame.K_s]:
            self.player.move(0, 1)
        if keys[pygame.K_a]:
            self.player.move(-1, 0)
        if keys[pygame.K_d]:
            self.player.move(1, 0)

        # Check for encounters if player moved
        if old_x != self.player.x or old_y != self.player.y:
            coords = (self.player.x, self.player.y)
            chunk = self.world.get_chunk(
                coords[0] // self.world.chunk_size, coords[1] // self.world.chunk_size
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

        return True

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        mode = (
            pygame.FULLSCREEN
            if self.fullscreen
            else (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        )
        self.screen = pygame.display.set_mode((0, 0) if self.fullscreen else mode)

    def render(self):
        if self.game_state == "menu":
            self.menu.render()
        elif self.game_state == "combat":
            self.combat_ui.draw_combat_scene(self.player, self.current_enemy)
        else:
            self.screen.fill(GameConfig.BLACK)
            screen_width, screen_height = self.screen.get_size()
            half_width = screen_width // (2 * GameConfig.GRID_SIZE)
            half_height = screen_height // (2 * GameConfig.GRID_SIZE)
            self._render_world(half_width, half_height)
            self._render_player(screen_width, screen_height)
        pygame.display.flip()

    def _render_world(self, half_width: int, half_height: int):
        px, py = self.player.x, self.player.y
        for y in range(-half_height, half_height + 1):
            for x in range(-half_width, half_width + 1):
                wx, wy = px + x, py + y
                chunk = self.world.get_chunk(
                    wx // self.world.chunk_size, wy // self.world.chunk_size
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
        player_font = next(iter(self.fonts.values()))
        player_text = player_font.render(
            GameConfig.PLAYER_SYMBOL, True, GameConfig.WHITE
        )
        player_x = screen_width // 2 - GameConfig.GRID_SIZE // 2
        player_y = screen_height // 2 - GameConfig.GRID_SIZE // 2
        self.screen.blit(player_text, (player_x, player_y))

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.render()
            self.clock.tick(GameConfig.FPS)
        pygame.quit()
