import random
import pygame
import numpy as np
from typing import Dict
from ...config.game_config import GameConfig
from ...config.font_config import FontConfig

class DisplayManager:
    def __init__(self):
        pygame.init()
        self.show_noise_map = False
        self.show_cell_borders = False
        self.clock = pygame.time.Clock()
        self.fonts = self._initialize_fonts()
        pygame.display.set_caption("Adventure")
        self.font_config = FontConfig(self.fonts)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render_debug_maps(self, debug_maps):
        """Renders debug visualization of noise maps"""
        if not debug_maps:
            return
        
        if hasattr(self, 'show_noise_map') and self.show_noise_map:
            # Convert noise map to pygame surface
            combined_map = debug_maps.get("combined")
            if combined_map is not None:
                # Scale values to 0-255 range and convert to uint8
                scaled_map = (combined_map * 255).astype('uint8')
                # Create RGB array by duplicating the grayscale values
                rgb_map = np.stack((scaled_map,) * 3, axis=-1)
                try:
                    surface = pygame.surfarray.make_surface(rgb_map)
                    self.screen.blit(surface, (0, 0))
                except ValueError as e:
                    print(f"Error creating debug surface: {e}")
                
        elif hasattr(self, 'show_cell_borders') and self.show_cell_borders:
            cell_borders = debug_maps.get("cell_borders")
            if cell_borders is not None:
                # Scale values to 0-255 range and convert to uint8  
                scaled_borders = (cell_borders * 255).astype('uint8')
                rgb_borders = np.stack((scaled_borders,) * 3, axis=-1)
                try:
                    surface = pygame.surfarray.make_surface(rgb_borders)
                    self.screen.blit(surface, (0, 0))
                except ValueError as e:
                    print(f"Error creating debug surface: {e}")

    def toggle_noise_map(self):
        self.show_noise_map = not self.show_noise_map
        self.show_cell_borders = False
        
    def toggle_cell_borders(self):
        self.show_cell_borders = not self.show_cell_borders
        self.show_noise_map = False

    def _initialize_fonts(self) -> Dict[str, pygame.font.Font]:
        fonts = {}
        for font_name in GameConfig.FONTS:
            fonts[font_name] = pygame.font.SysFont(font_name, GameConfig.GRID_SIZE)
        if not fonts:
            fonts["default"] = pygame.font.SysFont(None, GameConfig.GRID_SIZE)
        return fonts

    def toggle_fullscreen(self):
        is_fullscreen = bool(self.screen.get_flags() & pygame.FULLSCREEN)
        if is_fullscreen:
            self.screen = pygame.display.set_mode(
                (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
            )
        else:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    def render(self, game_state, world, player, ui_manager):
        self.screen.fill(GameConfig.BLACK)

        if game_state.current_state == "menu":
            ui_manager.menu.render()
        elif game_state.current_state == "combat":
            ui_manager.combat_ui.render(player, game_state.current_enemy)
        else:
            self._render_game_world(world, player)
            ui_manager.inventory_ui.render(player)
            ui_manager.combat_log.render()
            ui_manager.skill_tree_ui.render(game_state.skill_tree, player)  # Add this line

            if game_state.current_state == "level_up":
                ui_manager.level_up_ui.render(player.current_stats)

        pygame.display.flip()

    def _render_game_world(self, world, player):
        screen_width, screen_height = self.screen.get_size()
        half_width = screen_width // (2 * GameConfig.GRID_SIZE)
        half_height = screen_height // (2 * GameConfig.GRID_SIZE)
        
        self._render_terrain(world, player, half_width, half_height)
        self._render_player(screen_width, screen_height)

    def _render_terrain(self, world, player, half_width: int, half_height: int):
        px, py = player.x, player.y
        for y in range(-half_height, half_height + 1):
            for x in range(-half_width, half_width + 1):
                wx, wy = px + x, py + y
                chunk = world.get_chunk(
                    wx // world.chunk_size,
                    wy // world.chunk_size
                )
                local_x, local_y = (
                    wx % world.chunk_size,
                    wy % world.chunk_size,
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

    def get_screen_dimensions(self):
        return self.screen.get_size()

    def get_supported_char_and_font(self, biome_name: str, biome_data: dict) -> tuple[str, str]:
        font_name = self.font_config.get_valid_font_for_chars(biome_data["chars"])
        valid_chars = self.font_config.get_supported_chars(font_name, biome_data["chars"])
        
        if valid_chars:
            return random.choice(valid_chars), font_name
        return ".", next(iter(self.fonts.keys()))

    def cleanup(self):
        pygame.quit()