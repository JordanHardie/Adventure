import json
import os
from typing import Dict, Set

class FontConfig:
    def __init__(self, fonts):
        self.fonts = fonts
        self.glyph_support = self.load_glyph_support()

    def load_glyph_support(self) -> Dict[str, Set[str]]:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(
            os.path.join(script_dir, "font_support.json"), "r", encoding="utf-8"
        ) as f:
            return {k: set(v) for k, v in json.load(f).items()}

    def get_supported_chars(self, font_name: str, chars: list[str]) -> list[str]:
        """Return only the characters that are supported by the given font."""
        if font_name not in self.glyph_support:
            return []
        return [char for char in chars if char in self.glyph_support[font_name]]

    def get_valid_font_for_chars(self, chars: list[str]) -> str:
        """Find a font that supports all the given characters."""
        for font_name, supported_chars in self.glyph_support.items():
            if all(char in supported_chars for char in chars):
                return font_name
        return next(iter(self.glyph_support.keys()))  # Return first font as fallback
