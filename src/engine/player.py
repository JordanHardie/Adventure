from ..combat.entity import Entity, EntityType, Stats

class Player(Entity):
    def __init__(self, x: int = 0, y: int = 0):
        super().__init__("Player", EntityType.PLAYER, level=1)
        self.x = x
        self.y = y
        self.speed = 1
        self.base_stats = Stats(
            strength=5,
            defence=5,
            health=20,
            speed=5,
            stamina=15,
            dexterity=5,
            magic_power=5,
            magic_defence=5,
            wisdom=5,
            intelligence=5
        )
        self.initialize_stats()
        self.experience = 0
        self.next_level_exp = 100

    def move(self, dx: int, dy: int):
        self.x += dx * self.speed
        self.y += dy * self.speed

    def gain_experience(self, amount: int):
        self.experience += amount
        while self.experience >= self.next_level_exp:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.experience -= self.next_level_exp
        self.next_level_exp = int(self.next_level_exp * 1.5)
        self.initialize_stats()
