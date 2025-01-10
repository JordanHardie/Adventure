import noise
import numpy as np
from ..engine.generics import RandomUtils
from ..config.game_config import GameConfig

class TerrainGenerator:
    def __init__(self, seed: int = None):
        self.seed = seed or RandomUtils.int(0, 1_000_000)
        self.debug_mode = False

    def generate_noise_map(self, width: int, height: int, scale: float, base_x: int = 0, base_y: int = 0) -> np.ndarray:
        world_map = np.zeros((height, width))
        
        for y in range(height):
            for x in range(width):
                nx = (base_x + x) / scale
                ny = (base_y + y) / scale
                world_map[y, x] = noise.snoise2(nx, ny, base=self.seed)
                
        return (world_map + 1) / 2

    def generate_combined_map(self, width: int, height: int, base_pos: tuple) -> dict:
        # Generate individual noise maps
        temp_map = self.generate_noise_map(
            width, height, GameConfig.TEMPERATURE_SCALE,
            base_x=base_pos[0], base_y=base_pos[1]
        )
        humid_map = self.generate_noise_map(
            width, height, GameConfig.HUMIDITY_SCALE,
            base_x=base_pos[0], base_y=base_pos[1]
        )
        elev_map = self.generate_noise_map(
            width, height, GameConfig.ELEVATION_SCALE,
            base_x=base_pos[0], base_y=base_pos[1]
        )
        
        # Combine into RGB map
        rgb_map = np.zeros((height, width, 3))
        rgb_map[:,:,0] = temp_map  # Red channel for temperature
        rgb_map[:,:,1] = humid_map  # Green channel for humidity
        rgb_map[:,:,2] = elev_map  # Blue channel for elevation
        
        return {
            "combined": rgb_map,
            "temperature": temp_map,
            "humidity": humid_map,
            "elevation": elev_map
        }

    def generate_rivers(self, elevation_map: np.ndarray, width: int, height: int) -> np.ndarray:
        river_map = np.zeros((height, width))
        river_noise = self.generate_noise_map(width, height, GameConfig.RIVER_SCALE)
        river_potential = (1 - elevation_map) * river_noise
        river_map = river_potential > GameConfig.RIVER_THRESHOLD
        return river_map

    def generate_cell_borders(self, width: int, height: int, cell_size: int = 16) -> np.ndarray:
        border_map = np.zeros((height, width))
        
        # Draw vertical lines
        for x in range(0, width, cell_size):
            border_map[:, x] = 1
            
        # Draw horizontal lines
        for y in range(0, height, cell_size):
            border_map[y, :] = 1
            
        return border_map

    def get_debug_maps(self, width: int, height: int, base_pos: tuple):
        if not self.debug_mode:
            return None
            
        maps = self.generate_combined_map(width, height, base_pos)
        cell_borders = self.generate_cell_borders(width, height)
        maps["cell_borders"] = cell_borders
        
        return maps