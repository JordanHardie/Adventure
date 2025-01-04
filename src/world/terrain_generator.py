import random
import numpy as np
import noise
from ..config.game_config import GameConfig

class TerrainGenerator:
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 1_000_000)
        self.river_seeds = [random.randint(0, 1_000_000) for _ in range(3)]

    def generate_noise_map(
        self,
        width: int,
        height: int,
        scale: float,
        base_x: int = 0,
        base_y: int = 0,
        octaves: int = 1,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
    ) -> np.ndarray:
        world_map = np.zeros((height, width))

        for y in range(height):
            for x in range(width):
                nx, ny = (base_x + x) / scale, (base_y + y) / scale
                value = 0
                amplitude = 1
                frequency = 1
                max_amplitude = 0

                for _ in range(octaves):
                    value += amplitude * noise.snoise2(
                        nx * frequency, ny * frequency, base=self.seed
                    )
                    max_amplitude += amplitude
                    amplitude *= persistence
                    frequency *= lacunarity

                world_map[y, x] = value / max_amplitude

        return (world_map + 1) / 2

    def generate_rivers(
        self, elevation_map: np.ndarray, width: int, height: int
    ) -> np.ndarray:
        river_map = np.zeros((height, width))

        for _ in self.river_seeds:
            river_noise = self.generate_noise_map(
                width, height, GameConfig.RIVER_SCALE, octaves=2, persistence=0.5
            )
            river_potential = (1 - elevation_map) * river_noise
            river_mask = river_potential > GameConfig.RIVER_THRESHOLD
            river_map = np.maximum(river_map, river_mask)

        return river_map
