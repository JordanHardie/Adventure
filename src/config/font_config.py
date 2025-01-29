from typing import Dict, Set
from ..engine.generics import load_json_config

class FontConfig:
    def __init__(self, fonts):
        self.fonts = fonts
        self.glyph_support = self.load_glyph_support()

    def load_glyph_support(self) -> Dict[str, Set[str]]:
        font_data = load_json_config("font_support.json")
        return {k: set(v) for k, v in font_data.items()}

    def get_supported_chars(self, font_name: str, chars: list[str]) -> list[str]:
        if font_name not in self.glyph_support:
            return []
        return [char for char in chars if char in self.glyph_support[font_name]]

    def get_valid_font_for_chars(self, chars: list[str]) -> str:
        for font_name, supported_chars in self.glyph_support.items():
            if all(char in supported_chars for char in chars):
                return font_name
        return next(iter(self.glyph_support.keys()))