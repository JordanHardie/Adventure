import os
import json
import random
from typing import Any, Dict, List, Optional, TypeVar

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

class BaseUI:
    def __init__(self, screen):
        self.screen = screen
        self.visible = False
        
    def show(self):
        self.visible = True
        
    def hide(self):
        self.visible = False
        
    def toggle(self):
        self.visible = not self.visible
        
    def handle_input(self, *args, **kwargs):
        pass
        
    def render(self, *args, **kwargs):
        if not self.visible:
            return
            
    def handle_click(self, *args, **kwargs):
        if not self.visible:
            return False
        return True

    def handle_hover(self, *args, **kwargs):
        if not self.visible:
            return

T = TypeVar('T')

class RandomUtils:
    @staticmethod
    def set_seed(seed: int) -> None:
        random.seed(seed)

    @staticmethod
    def int(min_val: int, max_val: int) -> int:
        return random.randint(min_val, max_val)
    
    @staticmethod
    def float(min_val: float = 0.0, max_val: float = 1.0) -> float:
        return random.uniform(min_val, max_val)
        
    @staticmethod
    def chance(probability: float) -> bool:
        return random.random() < probability
        
    @staticmethod
    def choice(items: List[T]) -> T:
        return random.choice(items)

    @staticmethod
    def choices(items: List[T], weights: List[float] = None, k: int = 1) -> List[T]:
        return random.choices(items, weights=weights, k=k)

    @staticmethod   
    def sample(items: List[T], k: int) -> List[T]:
        return random.sample(items, k)

    @staticmethod
    def shuffle(items: List[Any]) -> None:
        random.shuffle(items)