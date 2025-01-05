import pygame
from typing import Optional, Tuple
from ..config.game_config import GameConfig
from ..engine.player import Player, ItemType, Item

class InventoryUI:
    """Manages the inventory interface and equipment management system."""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._init_fonts()
        self._init_layout()
        self.selected_item = None
        self.hovered_item = None
        self.visible = False

    def _init_fonts(self):
        """Initialize font settings."""
        self.font = pygame.font.SysFont(None, 32)
        self.large_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)  # For exp info

    def _init_layout(self):
        """Initialize UI layout and positions."""
        self.slot_size = 60
        self.padding = 10
        
        # Calculate window dimensions
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        self.window_width = min(750, self.screen_width - 40)
        self.window_height = min(600, self.screen_height - 40)
        self.window_x = (self.screen_width - self.window_width) // 2
        self.window_y = (self.screen_height - self.window_height) // 2
        
        self._init_equipment_slots()
        self._init_ring_slots()
        self._init_inventory_grid()

    def _init_equipment_slots(self):
        """Initialize equipment slot positions."""
        equip_start_x = self.window_x + 410
        equip_start_y = self.window_y + 25
        self.equipment_slots = {
            ItemType.HELMET: pygame.Rect(equip_start_x, equip_start_y, self.slot_size, self.slot_size),
            ItemType.TORSO: pygame.Rect(equip_start_x, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.BRACERS: pygame.Rect(equip_start_x - 70, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.GLOVES: pygame.Rect(equip_start_x + 70, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.LEGS: pygame.Rect(equip_start_x, equip_start_y + 140, self.slot_size, self.slot_size),
            ItemType.FEET: pygame.Rect(equip_start_x, equip_start_y + 210, self.slot_size, self.slot_size)
        }

    def _init_ring_slots(self):
        """Initialize ring slot positions."""
        ring_start_x = self.window_x + 605
        ring_start_y = self.window_y + 5
        self.ring_slots = []
        for i in range(10):
            x = ring_start_x + (i % 2) * (self.slot_size + 5)
            y = ring_start_y + (i // 2) * (self.slot_size + 5)
            self.ring_slots.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def _init_inventory_grid(self):
        """Initialize inventory grid layout."""
        cols, rows = 11, 4
        self.inventory_slots = []
        for row in range(rows):
            for col in range(cols):
                x = self.window_x + 20 + col * (self.slot_size + 5)
                y = self.window_y + 330 + row * (self.slot_size + 5)
                self.inventory_slots.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def toggle(self):
        """Toggle inventory visibility."""
        self.visible = not self.visible
        self.selected_item = None
        self.hovered_item = None

    def draw_item(self, item: Optional[Item], rect: pygame.Rect):
        """Draw an item slot and its contents."""
        color = (100, 100, 100) if item else (50, 50, 50)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, GameConfig.WHITE, rect, 2)
        
        if item:
            text = self.font.render(item.name[0], True, GameConfig.WHITE)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def draw_exp_info(self, player: Player, x: int, y: int):
        """Draw player level and experience information."""
        # Level
        level_text = self.font.render(f"Level {player.level}", True, GameConfig.WHITE)
        self.screen.blit(level_text, (x, y))
        
        # Experience progress
        exp_text = self.small_font.render(
            f"EXP: {player.experience}/{player.next_level_exp}", 
            True, GameConfig.WHITE
        )
        self.screen.blit(exp_text, (x, y + 30))
        
        # Progress bar
        bar_width = 150
        bar_height = 10
        progress = player.experience / player.next_level_exp
        
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y + 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y + 50, int(bar_width * progress), bar_height))

    def draw_stats(self, player: Player):
        """Draw player stats and resource bars."""
        x = self.window_x + 20
        y = self.window_y + 50
        stats = player.get_total_stats()
        
        # Draw experience info first
        self.draw_exp_info(player, x, y)
        y += 80  # Adjust starting position for resource bars
        
        # Resource bars
        bar_width = 150
        bar_height = 20
        bar_spacing = 25
        
        # HP Bar
        hp_percent = player.current_hp / player.max_hp
        pygame.draw.rect(self.screen, (50, 0, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (200, 0, 0), (x, y, int(bar_width * hp_percent), bar_height))
        hp_text = self.font.render(f"HP: {player.current_hp}/{player.max_hp}", True, GameConfig.WHITE)
        self.screen.blit(hp_text, (x + bar_width + 10, y))
        
        # MP Bar
        y += bar_spacing
        mp_percent = 1.0  # Placeholder
        pygame.draw.rect(self.screen, (0, 0, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 0, 200), (x, y, int(bar_width * mp_percent), bar_height))
        mp_text = self.font.render(f"MP: {100}/{100}", True, GameConfig.WHITE)
        self.screen.blit(mp_text, (x + bar_width + 10, y))
        
        # Stamina Bar
        y += bar_spacing
        sta_percent = player.current_stats.stamina / 100
        pygame.draw.rect(self.screen, (50, 50, 0), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (200, 200, 0), (x, y, int(bar_width * sta_percent), bar_height))
        sta_text = self.font.render(f"STA: {player.current_stats.stamina}/100", True, GameConfig.WHITE)
        self.screen.blit(sta_text, (x + bar_width + 10, y))
        
        # Stats display
        y += bar_spacing * 2
        stats_layout = [
            [("STR", stats.strength), ("SPD", stats.speed), ("MGP", stats.magic_power)],
            [("DEF", stats.defence), ("DEX", stats.dexterity), ("MGD", stats.magic_defence)],
            [("WIS", stats.wisdom), ("INT", stats.intelligence)]
        ]
        
        for row in stats_layout:
            line_text = " | ".join(f"{stat}: {value}" for stat, value in row)
            if len(row) < 3:  # Center the last row
                text = self.font.render(f"    {line_text}", True, GameConfig.WHITE)
            else:
                text = self.font.render(line_text, True, GameConfig.WHITE)
            self.screen.blit(text, (x, y))
            y += 25

    def draw_item_info(self):
        """Draw tooltip for hovered item."""
        if self.hovered_item:
            info_x = pygame.mouse.get_pos()[0] + 20
            info_y = pygame.mouse.get_pos()[1]
            
            # Background
            info_rect = pygame.Rect(info_x, info_y, 200, 150)
            pygame.draw.rect(self.screen, (0, 0, 0), info_rect)
            pygame.draw.rect(self.screen, GameConfig.WHITE, info_rect, 1)
            
            # Item details
            name_text = self.font.render(self.hovered_item.full_name, True, GameConfig.WHITE)
            self.screen.blit(name_text, (info_x + 5, info_y + 5))
            
            y_offset = 30
            for stat_name, value in self.hovered_item.stats.__dict__.items():
                if value > 0:
                    stat_text = self.font.render(f"{stat_name}: +{value}", True, GameConfig.WHITE)
                    self.screen.blit(stat_text, (info_x + 5, info_y + y_offset))
                    y_offset += 20

    def render(self, player: Player):
        """Render the inventory interface."""
        if not self.visible:
            return

        # Draw background
        window_rect = pygame.Rect(self.window_x, self.window_y, self.window_width, self.window_height)
        pygame.draw.rect(self.screen, (0, 0, 0), window_rect)
        pygame.draw.rect(self.screen, GameConfig.WHITE, window_rect, 2)

        # Draw title
        title = self.large_font.render("Inventory", True, GameConfig.WHITE)
        self.screen.blit(title, (self.window_x + 20, self.window_y + 10))

        # Draw equipment slots
        for slot_type, rect in self.equipment_slots.items():
            self.draw_item(player.inventory.equipped.get(slot_type), rect)

        # Draw ring slots
        for i, rect in enumerate(self.ring_slots):
            self.draw_item(player.inventory.rings[i], rect)

        # Draw inventory grid
        for i, rect in enumerate(self.inventory_slots):
            item = player.inventory.items[i] if i < len(player.inventory.items) else None
            self.draw_item(item, rect)

        # Draw stats
        self.draw_stats(player)

        # Draw tooltip for hovered item
        if self.hovered_item:
            self.draw_item_info()

    def handle_click(self, player: Player, pos: Tuple[int, int]) -> bool:
        """Handle mouse clicks on inventory items."""
        if not self.visible:
            return False

        # Check equipment slots
        for slot_type, rect in self.equipment_slots.items():
            if rect.collidepoint(pos):
                if self.selected_item:
                    if self.selected_item.item_type == slot_type:
                        old_item = player.inventory.equip(self.selected_item)
                        if old_item:
                            player.inventory.items.append(old_item)
                        player.inventory.items.remove(self.selected_item)
                        self.selected_item = None
                else:
                    item = player.inventory.equipped.get(slot_type)
                    if item:
                        player.inventory.unequip(slot_type)
                        player.inventory.items.append(item)
                return True

        # Check ring slots
        if self._handle_ring_slots(player, pos):
            return True

        # Check inventory slots
        if self._handle_inventory_slots(player, pos):
            return True

        return False

    def _handle_ring_slots(self, player: Player, pos: Tuple[int, int]) -> bool:
        """Handle interaction with ring slots."""
        for i, rect in enumerate(self.ring_slots):
            if rect.collidepoint(pos):
                if self.selected_item and self.selected_item.item_type == ItemType.RING:
                    old_item = player.inventory.equip(self.selected_item, i)
                    if old_item:
                        player.inventory.items.append(old_item)
                    player.inventory.items.remove(self.selected_item)
                    self.selected_item = None
                else:
                    item = player.inventory.rings[i]
                    if item:
                        player.inventory.unequip(ItemType.RING, i)
                        player.inventory.items.append(item)
                return True
        return False

    def _handle_inventory_slots(self, player: Player, pos: Tuple[int, int]) -> bool:
        """Handle interaction with inventory grid slots."""
        for i, rect in enumerate(self.inventory_slots):
            if rect.collidepoint(pos):
                if i < len(player.inventory.items):
                    if self.selected_item:
                        self.selected_item = None
                    else:
                        self.selected_item = player.inventory.items[i]
                return True
        return False

    def handle_hover(self, player: Player, pos: Tuple[int, int]):
        """Update hover state for item tooltips."""
        if not self.visible:
            return

        self.hovered_item = None

        # Check equipment slots
        for slot_type, rect in self.equipment_slots.items():
            if rect.collidepoint(pos):
                self.hovered_item = player.inventory.equipped.get(slot_type)
                return

        # Check ring slots
        for i, rect in enumerate(self.ring_slots):
            if rect.collidepoint(pos):
                self.hovered_item = player.inventory.rings[i]
                return

        # Check inventory slots
        for i, rect in enumerate(self.inventory_slots):
            if rect.collidepoint(pos) and i < len(player.inventory.items):
                self.hovered_item = player.inventory.items[i]
                return