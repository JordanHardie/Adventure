import random
import numpy as np
from scipy.ndimage import gaussian_filter
from typing import Dict, Tuple

from ..config.game_config import GameConfig
from ..config.font_config import FontConfig
from .world_chunk import WorldChunk
from .terrain_generator import TerrainGenerator

class World:
    """
    Manages the game world generation and chunk loading.
    Handles biome determination, terrain features, and font rendering.
    """

    def __init__(self, engine, chunk_size: int = 20):
        self.chunk_size = chunk_size
        self.chunks: Dict[Tuple[int, int], WorldChunk] = {}
        self.generator = TerrainGenerator()
        self.biomes = GameConfig.load_biomes()
        self.game_engine = engine
        self.font_config = FontConfig(engine.fonts)

    def _get_supported_char_and_font(self, biome_name: str) -> Tuple[str, str]:
        """Get a random supported character and font for the given biome."""
        biome = self.biomes[biome_name]
        font_name = self.font_config.get_valid_font_for_chars(biome["chars"])
        valid_chars = self.font_config.get_supported_chars(font_name, biome["chars"])
        
        if valid_chars:
            return random.choice(valid_chars), font_name
        return ".", next(iter(self.game_engine.fonts.keys()))

    def get_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        """Retrieve or generate a world chunk at the given coordinates."""
        chunk_key = (chunk_x, chunk_y)
        return self.chunks.get(chunk_key) or self._generate_chunk(chunk_x, chunk_y)

    def get_tile(self, world_x: int, world_y: int) -> tuple:
        """Get tile information at global world coordinates."""
        chunk_x, local_x = divmod(world_x, self.chunk_size)
        chunk_y, local_y = divmod(world_y, self.chunk_size)
        return self.get_chunk(chunk_x, chunk_y).terrain[local_y][local_x]

    def _adjust_color(self, base_color: list, params: dict) -> tuple:
        """Adjust tile color based on environmental parameters."""
        color = list(base_color)
        brightness = 1.0 + (params["elevation"] - 0.5) * 0.4
        color = [int(c * brightness) for c in color]

        # Environmental influences
        color[2] = min(255, color[2] + int(params["humidity"] * 20))
        color[0] = min(255, color[0] + int(params["temperature"] * 20))

        return tuple(min(255, max(0, c)) for c in color)

    def _generate_chunk(self, chunk_x: int, chunk_y: int) -> WorldChunk:
        """Generate a new chunk at the given coordinates."""
        chunk = WorldChunk(self.chunk_size)
        base_pos = (chunk_x * self.chunk_size, chunk_y * self.chunk_size)

        # Generate terrain maps
        elevation = self._generate_terrain_maps(base_pos)
        climate = self._generate_climate_maps(base_pos)
        rivers = self.generator.generate_rivers(
            elevation["base"], self.chunk_size, self.chunk_size
        )

        # Generate tiles
        for y in range(self.chunk_size):
            for x in range(self.chunk_size):
                biome = self._determine_biome(
                    climate, elevation, rivers, x, y, chunk_x, chunk_y
                )
                tile_data = self._generate_tile(biome)
                chunk.set_tile(x, y, *tile_data)

        self.chunks[(chunk_x, chunk_y)] = chunk
        return chunk

    def _generate_terrain_maps(self, base_pos: tuple) -> dict:
        """Generate elevation, mountain, and coastal terrain maps."""
        elevation = self.generator.generate_noise_map(
            self.chunk_size,
            self.chunk_size,
            GameConfig.ELEVATION_SCALE,
            base_x=base_pos[0],
            base_y=base_pos[1],
            octaves=4,
            persistence=0.5,
            lacunarity=2.0,
        )

        mountain = self.generator.generate_noise_map(
            self.chunk_size,
            self.chunk_size,
            GameConfig.ELEVATION_SCALE * 2,
            base_x=base_pos[0],
            base_y=base_pos[1],
            octaves=2,
        )

        coast = self.generator.generate_noise_map(
            self.chunk_size,
            self.chunk_size,
            GameConfig.ELEVATION_SCALE * 3,
            base_x=base_pos[0],
            base_y=base_pos[1],
        )

        # Apply terrain modifiers
        elevation = np.where(mountain > 0.6, elevation * 1.5, elevation)
        elevation = np.where(coast < 0.4, elevation * 0.5, elevation)
        elevation = gaussian_filter(elevation, sigma=1.5)

        return {"base": elevation, "mountain": mountain, "coast": coast}

    def _generate_climate_maps(self, base_pos: tuple) -> dict:
        """Generate temperature and humidity maps."""
        temperature = self.generator.generate_noise_map(
            self.chunk_size,
            self.chunk_size,
            GameConfig.TEMPERATURE_SCALE,
            base_x=base_pos[0],
            base_y=base_pos[1],
            octaves=2,
            persistence=0.6,
        )

        humidity = self.generator.generate_noise_map(
            self.chunk_size,
            self.chunk_size,
            GameConfig.HUMIDITY_SCALE,
            base_x=base_pos[0],
            base_y=base_pos[1],
            octaves=2,
            persistence=0.6,
        )

        # Smooth climate maps
        temperature = gaussian_filter(temperature, sigma=2.0)
        humidity = gaussian_filter(humidity, sigma=2.0)

        return {"temperature": temperature, "humidity": humidity}

    def _determine_biome(
        self,
        climate: dict,
        elevation: dict,
        rivers: np.ndarray,
        x: int,
        y: int,
        chunk_x: int,
        chunk_y: int,
    ) -> str:
        """Determine the biome type based on environmental factors."""
        # Check for water features first
        if rivers[y, x]:
            return "river"

        elev = elevation["base"][y, x]
        if elev < GameConfig.OCEAN_THRESHOLD:
            return "deep_ocean" if elev < GameConfig.OCEAN_THRESHOLD / 2 else "ocean"
        
        if elev < GameConfig.OCEAN_THRESHOLD + 0.05:
            return "beach"

        # Check for mountainous regions
        if elev > GameConfig.MOUNTAIN_THRESHOLD:
            temp = climate["temperature"][y, x]
            if temp < 0.3:
                return "snowy_peaks"
            if temp > 0.8:
                return "volcanic"
            return "mountain"

        # Calculate regional climate variations
        temp_offset, humid_offset = self._calculate_climate_offsets(chunk_x, chunk_y)
        temp = climate["temperature"][y, x] + temp_offset
        humid = climate["humidity"][y, x] + humid_offset

        return self._select_biome_by_climate(temp, humid, elev)

    def _calculate_climate_offsets(self, chunk_x: int, chunk_y: int) -> Tuple[float, float]:
        """Calculate regional temperature and humidity offsets."""
        cell_x = int(chunk_x * self.chunk_size / 2)
        cell_y = int(chunk_y * self.chunk_size / 2)

        temp_offset = (
            self.generator.generate_noise_map(
                1, 1, GameConfig.BIOME_SCALE * 2,
                base_x=cell_x, base_y=cell_y, octaves=1
            )[0][0] * 0.2
        )

        humid_offset = (
            self.generator.generate_noise_map(
                1, 1, GameConfig.BIOME_SCALE * 2,
                base_x=cell_x + 1000, base_y=cell_y + 1000, octaves=1
            )[0][0] * 0.2
        )

        return temp_offset, humid_offset

    def _select_biome_by_climate(self, temp: float, humid: float, elev: float) -> str:
        """Select appropriate biome based on climate conditions."""
        if temp < 0.3:
            valid_biomes = ["tundra", "taiga"]
        elif temp > 0.7:
            valid_biomes = ["desert", "savanna", "volcanic", "rainforest"]
        else:
            valid_biomes = ["grassland", "forest", "swamp"]

        for biome in valid_biomes:
            if biome in ["ocean", "deep_ocean", "beach", "river"]:
                continue

            params = self.biomes[biome]
            if "elevation" in params:
                e_min, e_max = params["elevation"]
                if not e_min <= elev <= e_max:
                    continue

            h_min, h_max = params["humidity"]
            t_min, t_max = params["temperature"]

            if h_min <= humid <= h_max and t_min <= temp <= t_max:
                return biome

        return "grassland"

    def _generate_tile(self, biome: str) -> tuple:
        """Generate tile appearance based on biome type."""
        biome_data = self.biomes[biome]
        char = random.choice(biome_data["chars"])
        color = list(random.choice(biome_data["colors"]))

        # Add slight color variation
        for i in range(3):
            color[i] = min(255, max(0, color[i] + random.randint(-10, 10)))

        return (char, tuple(color)), random.choice(list(self.game_engine.fonts.keys())), biome