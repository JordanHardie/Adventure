from typing import Optional
from ...engine.player import Player
from ...engine.generics import load_game_data, RandomUtils

class GameState:
    def __init__(self, display_manager, ui_manager, systems):
        self.world = None
        self.fullscreen = True
        self.systems = systems
        self.current_enemy = None
        self.current_state = "menu"
        self.ui_manager = ui_manager
        self.player: Optional[Player] = None 
        self.display_manager = display_manager
        self.skill_tree = self.systems.combat_system.skill_tree

    def set_world(self, world):
        self.world = world

    def transition_to(self, new_state: str):
        self.current_state = new_state
        if new_state == "combat":
            self.ui_manager.combat_ui.visible = True
            self.ui_manager.inventory_ui.visible = False
            self.ui_manager.combat_log.visible = False
        elif new_state == "game":
            self.ui_manager.combat_ui.visible = False
            self.ui_manager.inventory_ui.visible = False
            self.ui_manager.combat_log.visible = True

    def new_game(self):
        self.player = Player()
        self.transition_to("game")

    def continue_game(self):
        save_data = load_game_data()
        if save_data:
            x, y = save_data.get('x', 0), save_data.get('y', 0)
            self.player = Player(x, y)
            self.transition_to("game")

    def end_combat(self, message: str):
        self.ui_manager.combat_ui.add_to_log(message)
        self.transition_to("game")

    def process_combat_action(self, action: str) -> bool:
        self.ui_manager.show_combat_ui()

        result = self.systems.combat_system.process_turn(
            self.player, 
            self.current_enemy, 
            action
        )
        
        self.ui_manager.combat_ui.add_to_log(result["message"])

        if self.current_enemy.current_hp <= 0:
            self.handle_enemy_defeat(result)
            return True
        elif self.player.current_hp <= 0:
            self.ui_manager.combat_ui.add_to_log("You were defeated!")
            self.transition_to("menu")
            
        return True

    def handle_enemy_defeat(self, combat_result: dict):
        exp_gain = self._calculate_exp_gain()
        self.ui_manager.combat_ui.add_to_log(f"Gained {exp_gain} experience!")
        self.ui_manager.combat_log.add_message(
            f"Defeated {self.current_enemy.name}! +{exp_gain} exp"
        )

        if combat_result.get("loot"):
            self._handle_loot(combat_result["loot"])

        if self.player.gain_experience(exp_gain):
            # Add skill points to the skill tree when leveling up
            skill_points_gained = 2  # Or whatever number you want to give per level
            self.ui_manager.combat_log.add_message(f"Level Up! Gained {skill_points_gained} skill points!")
            self.skill_tree.add_skill_points(skill_points_gained)
            self.player.skill_points = 0  # Reset after adding to skill tree

            self.ui_manager.level_up_ui.show(5)
            self.transition_to("level_up")
        else:
            self.transition_to("game")

    def _calculate_exp_gain(self) -> int:
        base_exp = self.current_enemy.level * 10
        level_bonus = self.current_enemy.level + self.current_enemy.meta_level
        random_bonus = self.current_enemy.level * (2 + RandomUtils.int(0, 3))
        return base_exp + level_bonus + random_bonus

    def _handle_loot(self, loot: dict):
        if loot["items"]:
            for item in loot["items"]:
                self.player.inventory.items.append(item)
        self.player.inventory.gold += loot["gold"]
        self.ui_manager.combat_log.add_loot_message(loot["items"], loot["gold"])