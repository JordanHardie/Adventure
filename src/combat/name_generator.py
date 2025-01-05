import random
from ..engine.generics import load_json_config

class NameGenerator:
    def __init__(self):
        self.prefixes = load_json_config("prefixes.json")
        self.descriptions = load_json_config("descriptions.json")
        self.the_categories = ["creatures", "planes", "locations", "materials"]

    def generate_name(self, base_name: str, quality: int) -> str:
        prefix = random.choice(self.prefixes[str(quality)])
        
        if random.random() < 0.5:
            category = random.choice(list(self.descriptions.keys()))
            description = random.choice(self.descriptions[category])
            
            if category in self.the_categories:
                description = f"the {description}"
            
            return f"{prefix} {base_name} of {description}"
        
        return f"{prefix} {base_name}"