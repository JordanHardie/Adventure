import random
import json
import os

class NameGenerator:
    """Generates names for items using quality-based prefixes and random descriptions."""
    
    def __init__(self):
        self.prefixes = self._load_json("prefixes.json")
        self.descriptions = self._load_json("descriptions.json")
        
        # Categories that need "the" prefix
        self.the_categories = ["creatures", "planes", "locations", "materials"]

    def _load_json(self, filename: str) -> dict:
        """Load configuration from JSON file."""
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        with open(os.path.join(script_dir, "src", "config", filename), "r") as f:
            return json.load(f)

    def generate_name(self, base_name: str, quality: int) -> str:
        """Generate a full item name using prefix and description."""
        prefix = random.choice(self.prefixes[str(quality)])
        
        # 50% chance for "of" description
        if random.random() < 0.5:
            category = random.choice(list(self.descriptions.keys()))
            description = random.choice(self.descriptions[category])
            
            # Add "the" for specific categories
            if category in self.the_categories:
                description = f"the {description}"
            
            return f"{prefix} {base_name} of {description}"
        
        return f"{prefix} {base_name}"