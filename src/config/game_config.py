from ..engine.generics import load_json_config

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
        return load_json_config("biomes.json")
