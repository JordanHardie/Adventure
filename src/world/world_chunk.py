class WorldChunk:
    def __init__(self, size: int):
        self.size = size
        self.terrain = [[(".", (0, 255, 0)) for _ in range(size)] for _ in range(size)]
        self.fonts = [[None for _ in range(size)] for _ in range(size)]
        self.biomes = [[None for _ in range(size)] for _ in range(size)]

    def set_tile(self, x, y, tile, font_name, biome):
        self.terrain[y][x] = tile
        self.fonts[y][x] = font_name
        self.biomes[y][x] = biome

    def get_biome(self, x, y) -> str:
        return self.biomes[y][x]
