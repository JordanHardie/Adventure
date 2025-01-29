import threading
import numpy as np
from typing import Dict, Tuple
from scipy.ndimage import gaussian_filter
from concurrent.futures import ThreadPoolExecutor

from .world_chunk import WorldChunk
from .terrain_generator import TerrainGenerator

from ..engine.generics import RandomUtils
from ..config.game_config import GameConfig

class ChunkCache:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.chunks: Dict[Tuple[int, int], WorldChunk] = {}
        self._lock = threading.Lock()
        
    def get(self, key: Tuple[int, int]) -> WorldChunk:
        with self._lock:
            return self.chunks.get(key)
            
    def set(self, key: Tuple[int, int], chunk: WorldChunk):
        with self._lock:
            if len(self.chunks) >= self.max_size:
                self.chunks.pop(next(iter(self.chunks)))
            self.chunks[key] = chunk

class World:
    def __init__(self, engine, chunk_size: int = 20):
        self.biomes = {}
        self._font_cache = {}
        self.game_engine = engine
        self.chunk_size = chunk_size
        self.chunk_cache = ChunkCache()
        self.generator = TerrainGenerator()
        self.terrain_executor = ThreadPoolExecutor(max_workers=2)
        self.chunk_executor = ThreadPoolExecutor(max_workers=4)
        
        self._font_lock = threading.Lock()

    def _load_biomes(self):
        if not self.biomes:
            self.biomes = GameConfig.load_biomes()
        return self.biomes

    def get_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        chunk_key = (chunk_x, chunk_y)
        chunk = self.chunk_cache.get(chunk_key)
        if chunk is None:
            chunk = self._generate_chunk(chunk_x, chunk_y)
            self.chunk_cache.set(chunk_key, chunk)
        return chunk

    def get_tile(self, world_x: int, world_y: int) -> tuple:
        chunk_x, local_x = divmod(world_x, self.chunk_size)
        chunk_y, local_y = divmod(world_y, self.chunk_size)
        return self.get_chunk(chunk_x, chunk_y).terrain[local_y][local_x]

    def _generate_terrain_maps(self, base_pos: tuple) -> Dict[str, np.ndarray]:
        elevation = self.generator.generate_noise_map(
            self.chunk_size, self.chunk_size, 
            GameConfig.ELEVATION_SCALE,
            base_x=base_pos[0], base_y=base_pos[1]
        )
    
        mountain = self.generator.generate_noise_map(
            self.chunk_size, self.chunk_size,
            GameConfig.ELEVATION_SCALE * 2,
            base_x=base_pos[0], base_y=base_pos[1]
        )
    
        coast = self.generator.generate_noise_map(
            self.chunk_size, self.chunk_size,
            GameConfig.ELEVATION_SCALE * 3,
            base_x=base_pos[0], base_y=base_pos[1]
        )

        elevation = np.where(mountain > 0.6, elevation * 1.5, elevation)
        elevation = np.where(coast < 0.4, elevation * 0.5, elevation)
        elevation = gaussian_filter(elevation, sigma=1.5)
    
        return {"base": elevation, "mountain": mountain, "coast": coast}

    def _generate_climate_maps(self, base_pos: tuple) -> Dict[str, np.ndarray]:
        futures = []
        scales = [GameConfig.TEMPERATURE_SCALE, GameConfig.HUMIDITY_SCALE]
    
        for scale in scales:
            futures.append(self.terrain_executor.submit(
                self.generator.generate_noise_map,
                self.chunk_size, self.chunk_size, scale,
                base_x=base_pos[0], base_y=base_pos[1]
            ))
        
        temp_map, humid_map = [gaussian_filter(f.result(), sigma=2.0) for f in futures]
        return {"temperature": temp_map, "humidity": humid_map}

    def _determine_biome(self, climate: Dict, elevation: Dict, rivers: np.ndarray, x: int, y: int) -> str:
        params = {
            "elevation": elevation["base"][y, x],
            "temperature": climate["temperature"][y, x],
            "humidity": climate["humidity"][y, x]
        }

        if rivers[y, x] > GameConfig.RIVER_THRESHOLD:
            return "river"

        candidates = []
        for biome_name, requirements in self.biomes.items():
            if (requirements["elevation"][0] <= params["elevation"] <= requirements["elevation"][1] and
                requirements["temperature"][0] <= params["temperature"] <= requirements["temperature"][1] and
                requirements["humidity"][0] <= params["humidity"] <= requirements["humidity"][1]):
                candidates.append(biome_name)

        return candidates[0] if candidates else "grassland"

    def _generate_tile(self, biome: str, params: dict) -> tuple:
        if not self.biomes:
            self.biomes = self._load_biomes()
        biome_data = self.biomes[biome]
        char = self._get_valid_char(biome_data["chars"])
        color = list(self._get_valid_color(biome_data["colors"]))
        return (char, tuple(self._adjust_color(color, params))), self._get_font_name(char), biome

    def _get_valid_char(self, chars: list) -> str:
        with self._font_lock:
            # Randomly select a character from the list
            char = RandomUtils.choice(chars)
        
            # Ensure the font exists for this character
            if char not in self._font_cache:
                self._font_cache[char] = True
        
            return char

    def _get_valid_color(self, colors: list) -> tuple:
        return [max(0, min(255, c + np.random.randint(-10, 11))) for c in colors[0]]

    def _adjust_color(self, color: list, params: dict) -> list:
        brightness = 1.0 + (params["elevation"] - 0.5) * 0.4
        color = [int(c * brightness) for c in color]
        color[2] = min(255, color[2] + int(params["humidity"] * 20))
        color[0] = min(255, color[0] + int(params["temperature"] * 20))
        return [min(255, max(0, c)) for c in color]

    def _get_font_name(self, char: str) -> str:
        return RandomUtils.choice(list(self.game_engine.fonts.keys()))

    def _generate_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        chunk = WorldChunk(self.chunk_size)
        base_pos = (chunk_x * self.chunk_size, chunk_y * self.chunk_size)

        elevation = self._generate_terrain_maps(base_pos)
        climate = self._generate_climate_maps(base_pos)
        rivers = self.generator.generate_rivers(elevation["base"], self.chunk_size, self.chunk_size)

        futures = []
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                biome = self._determine_biome(climate, elevation, rivers, x, y)
                params = {
                    "elevation": elevation["base"][y, x],
                    "temperature": climate["temperature"][y, x],
                    "humidity": climate["humidity"][y, x]
                }
                futures.append((x, y, self.chunk_executor.submit(self._generate_tile, biome, params)))

        for x, y, future in futures:
            tile_data = future.result()
            chunk.set_tile(x, y, *tile_data)

        return chunk

    def __del__(self):
        self.terrain_executor.shutdown()
        self.chunk_executor.shutdown()