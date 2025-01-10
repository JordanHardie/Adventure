import pygame
from typing import Dict
from ...engine.generics import save_game_data

class InputProcessor:
    def process(self, game_state, event: pygame.event.Event) -> bool:
        """Process an event and return False if game should exit"""
        return True

class MenuInputProcessor(InputProcessor):
    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key in [pygame.K_UP, pygame.K_DOWN]:
                game_state.ui_manager.menu.selected = (game_state.ui_manager.menu.selected + 1) % 2
            if event.key == pygame.K_RETURN:
                if game_state.ui_manager.menu.selected == 0:
                    game_state.new_game()
                else:
                    game_state.continue_game()
        return True

class GameInputProcessor(InputProcessor):
    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if game_state.ui_manager.inventory_ui.visible:
                game_state.ui_manager.inventory_ui.handle_click(game_state.player, pos, True)
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if game_state.ui_manager.inventory_ui.visible:
                game_state.ui_manager.inventory_ui.handle_click(game_state.player, pos, False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                save_game_data({'x': game_state.player.x, 'y': game_state.player.y})
                game_state.transition_to("menu")
            elif event.key == pygame.K_F11:
                game_state.display_manager.toggle_fullscreen()
            elif event.key == pygame.K_i:
                game_state.ui_manager.inventory_ui.toggle()
            elif event.key == pygame.K_LSHIFT:
                game_state.player.speed = 2
        elif event.type == pygame.KEYUP and event.key == pygame.K_LSHIFT:
            game_state.player.speed = 1

        return True

class CombatInputProcessor(InputProcessor):
    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                game_state.ui_manager.combat_ui.selected_action = (
                    game_state.ui_manager.combat_ui.selected_action - 1
                ) % len(game_state.ui_manager.combat_ui.actions)
            elif event.key == pygame.K_RIGHT:
                game_state.ui_manager.combat_ui.selected_action = (
                    game_state.ui_manager.combat_ui.selected_action + 1
                ) % len(game_state.ui_manager.combat_ui.actions)
            elif event.key == pygame.K_RETURN:
                action = game_state.ui_manager.combat_ui.actions[
                    game_state.ui_manager.combat_ui.selected_action
                ].lower()
                if action == "run":
                    game_state.end_combat("Got away safely!")
                    return True
                return game_state.process_combat_action(action)
        return True

class LevelUpInputProcessor(InputProcessor):
    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                game_state.ui_manager.level_up_ui.selected_stat = (
                    game_state.ui_manager.level_up_ui.selected_stat - 1
                ) % len(game_state.ui_manager.level_up_ui.stats)
            elif event.key == pygame.K_DOWN:
                game_state.ui_manager.level_up_ui.selected_stat = (
                    game_state.ui_manager.level_up_ui.selected_stat + 1
                ) % len(game_state.ui_manager.level_up_ui.stats)
            elif event.key == pygame.K_RETURN and game_state.ui_manager.level_up_ui.points_available > 0:
                self._process_level_up(game_state)
        return True

    def _process_level_up(self, game_state):
        level_up_ui = game_state.ui_manager.level_up_ui
        stat_name = level_up_ui.stats[level_up_ui.selected_stat]
        current = getattr(game_state.player.base_stats, stat_name)
        setattr(game_state.player.base_stats, stat_name, current + 1)
        level_up_ui.points_available -= 1
        game_state.player.initialize_stats()
        
        if level_up_ui.points_available == 0:
            level_up_ui.hide()
            game_state.transition_to("game")

class InputManager:
    def __init__(self):
        self.processors: Dict[str, InputProcessor] = {
            "menu": MenuInputProcessor(),
            "game": GameInputProcessor(),
            "combat": CombatInputProcessor(),
            "level_up": LevelUpInputProcessor()
        }

    def handle_input(self, game_state) -> bool:
        """Process all pending events for the current game state"""
        for event in pygame.event.get():
            if not self.processors[game_state.current_state].process(game_state, event):
                return False

        # Handle continuous key presses for movement
        if game_state.current_state == "game":
            if self._handle_movement(game_state):
                game_state.systems.encounter_system.check_encounters(game_state)

        return True

    def _handle_movement(self, game_state) -> bool:
        """Process player movement input. Returns True if player moved."""
        keys = pygame.key.get_pressed()
        old_x, old_y = game_state.player.x, game_state.player.y

        if keys[pygame.K_w]: game_state.player.move(0, -1)
        if keys[pygame.K_s]: game_state.player.move(0, 1)
        if keys[pygame.K_a]: game_state.player.move(-1, 0)
        if keys[pygame.K_d]: game_state.player.move(1, 0)

        return old_x != game_state.player.x or old_y != game_state.player.y

    def _handle_debug_keys(self, event, game_state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:  # Toggle noise map
                game_state.display_manager.toggle_noise_map()
            elif event.key == pygame.K_F4:  # Toggle cell borders
                game_state.display_manager.toggle_cell_borders()
            elif event.key == pygame.K_F5:  # Toggle debug mode
                game_state.world.generator.debug_mode = not game_state.world.generator.debug_mode