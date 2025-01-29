import pygame
from typing import Dict
from ...engine.generics import save_game_data
from ...engine.player import Item, ItemType, ItemStats

class InputProcessor:
    def process(self, game_state, event: pygame.event.Event) -> bool:
        """Process an event and return False if game should exit"""
        return True

class GameInputProcessor(InputProcessor):
    """Handles all input processing for the main game state"""
    
    def process(self, game_state, event: pygame.event.Event) -> bool:
        handlers = {
            pygame.QUIT: self._handle_quit,
            pygame.MOUSEBUTTONDOWN: self._handle_mouse_down,
            pygame.MOUSEBUTTONUP: self._handle_mouse_up,
            pygame.MOUSEMOTION: self._handle_mouse_motion,
            pygame.KEYDOWN: self._handle_keydown,
            pygame.KEYUP: self._handle_keyup
        }
        
        handler = handlers.get(event.type)
        if handler:
            return handler(game_state, event)
        return True

    def _handle_quit(self, game_state, event) -> bool:
        """Handle game quit event"""
        return False

    def _handle_mouse_down(self, game_state, event) -> bool:
        """Handle mouse button press events"""
        pos = pygame.mouse.get_pos()
        
        if game_state.ui_manager.inventory_ui.visible:
            game_state.ui_manager.inventory_ui.handle_click(game_state.player, pos, True)
        elif game_state.ui_manager.skill_tree_ui.visible:
            game_state.ui_manager.skill_tree_ui.handle_click(
                pos, 
                game_state.systems.combat_system.skill_tree, 
                game_state.player
            )
        return True

    def _handle_mouse_up(self, game_state, event) -> bool:
        """Handle mouse button release events"""
        if game_state.ui_manager.inventory_ui.visible:
            game_state.ui_manager.inventory_ui.handle_click(
                game_state.player, 
                pygame.mouse.get_pos(), 
                False
            )
        return True

    def _handle_mouse_motion(self, game_state, event) -> bool:
        """Handle mouse movement events"""
        pos = pygame.mouse.get_pos()

        if game_state.ui_manager.inventory_ui.visible:
            if hasattr(game_state.ui_manager.inventory_ui, 'handle_hover'):  # Add safety check
                game_state.ui_manager.inventory_ui.handle_hover(game_state.player, pos)
        return True

    def _handle_keydown(self, game_state, event: pygame.event.Event) -> bool:
        KEY_MAP = {
            pygame.K_1: ItemType.HELMET,
            pygame.K_2: ItemType.TORSO,
            pygame.K_3: ItemType.BRACERS,
            pygame.K_4: ItemType.GLOVES,
            pygame.K_5: ItemType.LEGS,
            pygame.K_6: ItemType.FEET,
            pygame.K_7: ItemType.WEAPON,
            pygame.K_0: "LEVEL_UP",
        }

        if event.mod & pygame.KMOD_CTRL:
            if event.key in KEY_MAP:
                if KEY_MAP[event.key] == "LEVEL_UP":
                    game_state.player.gain_experience(game_state.player.next_level_exp)
                    game_state.ui_manager.level_up_ui.show(5)
                    game_state.skill_tree.add_skill_points(2)
                    game_state.transition_to("level_up")
                    print(f"DEBUG: Forced level up to {game_state.player.level}")
                else:
                    item_stats = ItemStats(strength=5, defence=5, health=10, speed=5, stamina=10,
                                           magic_power=5, magic_defence=5, wisdom=5, intelligence=5)
                    new_item = Item(f"Debug {KEY_MAP[event.key].name}", KEY_MAP[event.key], 0, item_stats)
                    game_state.player.inventory.items.append(new_item)
                    print(f"DEBUG: Spawned {new_item.name}")
                return True

        key_handlers = {
            pygame.K_ESCAPE: GameInputProcessor._handle_escape,
            pygame.K_F11: GameInputProcessor._handle_fullscreen,
            pygame.K_i: GameInputProcessor._handle_inventory,
            pygame.K_k: GameInputProcessor._handle_skill_tree,
            pygame.K_LSHIFT: GameInputProcessor._handle_sprint,
            pygame.K_F3: GameInputProcessor._handle_noise_map,
            pygame.K_F4: GameInputProcessor._handle_cell_borders
        }

        handler = key_handlers.get(event.key)
        if handler:
            handler(game_state)
        return True

    def _handle_keyup(self, game_state, event) -> bool:
        """Handle keyboard key release events"""
        if event.key == pygame.K_LSHIFT:
            game_state.player.speed = 1
        return True

    @staticmethod
    def _handle_escape(game_state) -> bool:
        if game_state.ui_manager.skill_tree_ui.visible:
            game_state.ui_manager.skill_tree_ui.hide()
        elif game_state.ui_manager.inventory_ui.visible:
            game_state.ui_manager.inventory_ui.hide()
        else:
            save_game_data({'x': game_state.player.x, 'y': game_state.player.y})
            game_state.transition_to("menu")
        return True

    def _handle_fullscreen(self, game_state) -> bool:
        game_state.display_manager.toggle_fullscreen()
        return True

    @staticmethod
    def _handle_inventory(game_state):
        """Toggle inventory visibility"""
        if game_state.ui_manager.skill_tree_ui.visible:
            return
        game_state.ui_manager.inventory_ui.toggle()

    @staticmethod
    def _handle_skill_tree(game_state):
        """Toggle skill tree visibility"""
        if game_state.ui_manager.inventory_ui.visible:
            return
        game_state.ui_manager.skill_tree_ui.toggle()

    @staticmethod
    def _handle_sprint(game_state):
        """Enable sprint movement"""
        game_state.player.speed = 2

    @staticmethod
    def _handle_noise_map(game_state):
        """Toggle noise map debug view"""
        game_state.display_manager.show_noise_map = not game_state.display_manager.show_noise_map

    @staticmethod
    def _handle_cell_borders(game_state):
        """Toggle cell borders debug view"""
        game_state.display_manager.show_cell_borders = not game_state.display_manager.show_cell_borders

class MenuInputProcessor(InputProcessor):
    """Handles all input processing for the menu state"""

    def process(self, game_state, event: pygame.event.Event) -> bool:
        handlers = {
            pygame.QUIT: self._handle_quit,
            pygame.KEYDOWN: self._handle_keydown
        }
        
        handler = handlers.get(event.type)
        if handler:
            return handler(game_state, event)
        return True

    @staticmethod
    def _handle_quit(game_state) -> bool:
        """Handle quit event"""
        return False

    @staticmethod
    def _handle_keydown(game_state, event) -> bool:
        key_handlers = {
            pygame.K_ESCAPE: lambda x: MenuInputProcessor._handle_escape(x),
            pygame.K_UP: MenuInputProcessor._handle_menu_nav,
            pygame.K_DOWN: MenuInputProcessor._handle_menu_nav,
            pygame.K_RETURN: MenuInputProcessor._handle_selection
        }

        handler = key_handlers.get(event.key)
        if handler:
            return handler(game_state)
        return True

    @staticmethod
    def _handle_escape(game_state) -> bool:
        """Exit game on escape"""
        return False

    @staticmethod
    def _handle_menu_nav(game_state) -> bool:
        """Handle menu navigation (up/down)"""
        if game_state.ui_manager.menu.has_save():
            game_state.ui_manager.menu.selected = (game_state.ui_manager.menu.selected + 1) % 2
        return True

    @staticmethod
    def _handle_selection(game_state) -> bool:
        """Handle menu option selection"""
        if game_state.ui_manager.menu.selected == 0:
            game_state.new_game()
        else:
            game_state.continue_game()
        return True

class CombatInputProcessor(InputProcessor):
    """Handles all input processing for the combat state"""

    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.QUIT:
            return False
            
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(game_state, event)
            
        return True

    def _handle_keydown(self, game_state, event) -> bool:
        """Handle combat controls"""
        key_handlers = {
            pygame.K_LEFT: self._handle_action_select_left,
            pygame.K_RIGHT: self._handle_action_select_right,
            pygame.K_RETURN: self._handle_action_confirm
        }
        
        handler = key_handlers.get(event.key)
        if handler:
            return handler(game_state)
        return True

    @staticmethod
    def _handle_action_select_left(game_state) -> bool:
        """Select previous combat action"""
        game_state.ui_manager.combat_ui.selected_action = (
            game_state.ui_manager.combat_ui.selected_action - 1
        ) % len(game_state.ui_manager.combat_ui.actions)
        return True

    @staticmethod
    def _handle_action_select_right(game_state) -> bool:
        """Select next combat action"""
        game_state.ui_manager.combat_ui.selected_action = (
            game_state.ui_manager.combat_ui.selected_action + 1
        ) % len(game_state.ui_manager.combat_ui.actions)
        return True

    @staticmethod
    def _handle_action_confirm(game_state) -> bool:
        """Confirm selected combat action"""
        action = game_state.ui_manager.combat_ui.actions[
            game_state.ui_manager.combat_ui.selected_action
        ].lower()
        
        if action == "run":
            game_state.end_combat("Got away safely!")
            return True
            
        return game_state.process_combat_action(action)

class LevelUpInputProcessor(InputProcessor):
    """Handles all input processing for the level up state"""

    def process(self, game_state, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(game_state, event)
        return True

    def _handle_keydown(self, game_state, event) -> bool:
        """Handle level up menu controls"""
        key_handlers = {
            pygame.K_UP: self._handle_stat_select_up,
            pygame.K_DOWN: self._handle_stat_select_down,
            pygame.K_RETURN: self._handle_stat_confirm
        }
        
        handler = key_handlers.get(event.key)
        if handler:
            return handler(game_state)
        return True

    @staticmethod
    def _handle_stat_select_up(game_state) -> bool:
        """Select previous stat"""
        game_state.ui_manager.level_up_ui.selected_stat = (
            game_state.ui_manager.level_up_ui.selected_stat - 1
        ) % len(game_state.ui_manager.level_up_ui.stats)
        return True

    @staticmethod
    def _handle_stat_select_down(game_state) -> bool:
        """Select next stat"""
        game_state.ui_manager.level_up_ui.selected_stat = (
            game_state.ui_manager.level_up_ui.selected_stat + 1
        ) % len(game_state.ui_manager.level_up_ui.stats)
        return True

    @staticmethod
    def _handle_stat_confirm(game_state) -> bool:
        """Confirm stat point allocation"""
        if game_state.ui_manager.level_up_ui.points_available > 0:
            level_up_ui = game_state.ui_manager.level_up_ui
            stat_name = level_up_ui.stats[level_up_ui.selected_stat]
            
            # Increase the selected stat
            current = getattr(game_state.player.base_stats, stat_name)
            setattr(game_state.player.base_stats, stat_name, current + 1)
            
            # Update points and player stats
            level_up_ui.points_available -= 1
            game_state.player.initialize_stats()
            
            # Check if we're done leveling up
            if level_up_ui.points_available == 0:
                level_up_ui.hide()
                game_state.transition_to("game")
                
        return True

class InputManager:
    """Manages all input processing for different game states"""
    
    def __init__(self):
        # Initialize input processors for each game state
        self.processors: Dict[str, InputProcessor] = {
            "menu": MenuInputProcessor(),
            "game": GameInputProcessor(),
            "combat": CombatInputProcessor(),
            "level_up": LevelUpInputProcessor()
        }

    def handle_input(self, game_state) -> bool:
        """
        Process all pending events for the current game state
        Returns: False if game should exit, True otherwise
        """
        # Handle all pending events
        for event in pygame.event.get():
            if not self.processors[game_state.current_state].process(game_state, event):
                return False

        # Handle continuous movement input in game state
        if game_state.current_state == "game":
            if self._handle_movement(game_state):
                game_state.systems.encounter_system.check_encounters(game_state)

        if game_state.ui_manager.skill_tree_ui.visible:
            for event in pygame.event.get():
                if event.type in (pygame.MOUSEWHEEL, pygame.KEYDOWN):
                    game_state.ui_manager.skill_tree_ui.handle_scroll(event, game_state.skill_tree)

        return True

    @staticmethod
    def _handle_movement(game_state) -> bool:
        """
        Process player movement input
        Returns: True if player moved, False otherwise
        """
        keys = pygame.key.get_pressed()
        old_x, old_y = game_state.player.x, game_state.player.y

        # Check movement keys and update player position
        if keys[pygame.K_w]: game_state.player.move(0, -1)
        if keys[pygame.K_s]: game_state.player.move(0, 1)
        if keys[pygame.K_a]: game_state.player.move(-1, 0)
        if keys[pygame.K_d]: game_state.player.move(1, 0)

        # Return whether position changed
        return old_x != game_state.player.x or old_y != game_state.player.y