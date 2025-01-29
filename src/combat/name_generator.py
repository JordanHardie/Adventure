from ..engine.generics import load_json_config, RandomUtils

class NameGenerator:
    def __init__(self):
        self.prefixes = load_json_config("prefixes.json")
        self.descriptions = load_json_config("descriptions.json")
        self.the_categories = ["creatures", "planes", "locations", "materials"]

    def generate_name(self, base_name: str, quality: int) -> str:
        prefix = RandomUtils.choice(self.prefixes[str(quality)])
        
        if RandomUtils.chance(0.5):
            category = RandomUtils.choice(list(self.descriptions.keys()))
            description = RandomUtils.choice(self.descriptions[category])
            
            if category in self.the_categories:
                description = f"the {description}"
            
            return f"{prefix} {base_name} of {description}"
        
        return f"{prefix} {base_name}"