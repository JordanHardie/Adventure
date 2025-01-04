import os
import json

class GameConfig:
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    GRID_SIZE = 20
    FPS = 60

    BIOME_SCALE = 150.0
    ELEVATION_SCALE = 100.0
    RIVER_SCALE = 80.0
    TEMPERATURE_SCALE = 150.0
    HUMIDITY_SCALE = 120.0

    MOUNTAIN_THRESHOLD = 0.6
    RIVER_THRESHOLD = 0.8
    OCEAN_THRESHOLD = 0.2

    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    PLAYER_SYMBOL = "@"

    FONTS = [
        "cascadiaMonoNFRegular",
        "firaCode",
        "courierNew",
        "dejavuSansMono",
        "jetbrainsMono",
    ]

    @staticmethod
    def load_biomes():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "biomes.json"), "r", encoding="utf-8") as f:
            return json.load(f)
