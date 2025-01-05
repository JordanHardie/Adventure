import os
import json
from typing import Any, Dict, Optional

def get_project_root() -> str:
    """Get the root directory of the project."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_json_config(filename: str, subdirectory: str = "config") -> Dict[str, Any]:
    """
    Load a JSON configuration file from the config directory.
    
    Args:
        filename: Name of the JSON file
        subdirectory: Subdirectory within project (default: "config")
    """
    script_dir = get_project_root()
    file_path = os.path.join(script_dir, "src", subdirectory, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_game_data(data: Dict[str, Any], filename: str = "save.json") -> None:
    """Save game data to the appropriate directory."""
    save_dir = os.path.join(os.getenv('APPDATA'), 'Adventure')
    os.makedirs(save_dir, exist_ok=True)
    
    save_path = os.path.join(save_dir, filename)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def load_game_data(filename: str = "save.json") -> Optional[Dict[str, Any]]:
    """Load game data from save file."""
    save_path = os.path.join(os.getenv('APPDATA'), 'Adventure', filename)
    if os.path.exists(save_path):
        with open(save_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def calculate_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    """Calculate Euclidean distance between two points."""
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5