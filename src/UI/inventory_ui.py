import pygame
from typing import Optional, Tuple
from ..engine.generics import RandomUtils
from ..config.game_config import GameConfig
from ..engine.player import Player, ItemType, Item

class InventoryUI:
    def __init__(self, screen: pygame.Surface, combat_log=None):
        self.screen = screen
        self.combat_log = combat_log
        self._init_fonts()
        self._init_layout()
        self.selected_item = None
        self.hovered_item = None
        self.visible = False
        self.dragging = False
        self.drag_start_pos = None
        self._init_item_symbols()
        self._init_quality_colors()

    def hide(self):
        self.visible = False

    def sell_item(self, player: Player, item: Item) -> None:
        sell_value = (item.quality + 1) * 10 + RandomUtils.int(5, 15)
        player.inventory.gold += sell_value
    
        if item in player.inventory.items:
            player.inventory.items.remove(item)
        
        if self.combat_log:
            self.combat_log.add_message(f"Sold {item.name} for {sell_value} gold")

    def _init_item_symbols(self):
        self.item_symbols = {
            ItemType.WEAPON: "†",
            ItemType.HELMET: "o",
            ItemType.TORSO: "T",
            ItemType.BRACERS: "=",
            ItemType.GLOVES: ")",
            ItemType.RING: "°",
            ItemType.LEGS: "‖",
            ItemType.FEET: "_",
        }

    def _init_quality_colors(self):
        self.quality_colors = [
            (128, 128, 128),  # Gray
            (255, 255, 255),  # White
            (30, 255, 0),     # Green
            (0, 112, 255),    # Blue
            (163, 53, 238),   # Purple
        ]

    def _init_fonts(self):
        self.font = pygame.font.SysFont(None, 32)
        self.large_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 24)

    def _init_layout(self):
        self.slot_size = 60
        self.padding = 10
        
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
        equip_start_x = self.window_x + 460
        equip_start_y = self.window_y + 45
        self.equipment_slots = {
            ItemType.WEAPON: pygame.Rect(equip_start_x - 140, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.HELMET: pygame.Rect(equip_start_x, equip_start_y, self.slot_size, self.slot_size),
            ItemType.TORSO: pygame.Rect(equip_start_x, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.BRACERS: pygame.Rect(equip_start_x - 70, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.GLOVES: pygame.Rect(equip_start_x + 70, equip_start_y + 70, self.slot_size, self.slot_size),
            ItemType.LEGS: pygame.Rect(equip_start_x, equip_start_y + 140, self.slot_size, self.slot_size),
            ItemType.FEET: pygame.Rect(equip_start_x, equip_start_y + 210, self.slot_size, self.slot_size)
        }

    def _init_ring_slots(self):
        ring_start_x = self.window_x + 605
        ring_start_y = self.window_y + 5
        self.ring_slots = []
        for i in range(10):
            x = ring_start_x + (i % 2) * (self.slot_size + 5)
            y = ring_start_y + (i // 2) * (self.slot_size + 5)
            self.ring_slots.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def _init_inventory_grid(self):
        cols, rows = 11, 4
        self.inventory_slots = []
        for row in range(rows):
            for col in range(cols):
                x = self.window_x + 20 + col * (self.slot_size + 5)
                y = self.window_y + 330 + row * (self.slot_size + 5)
                self.inventory_slots.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def toggle(self):
        self.visible = not self.visible
        self.selected_item = None
        self.hovered_item = None
        self.dragging = False

    def draw_item(self, item: Optional[Item], rect: pygame.Rect):
        color = (100, 100, 100) if item else (50, 50, 50)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, GameConfig.WHITE, rect, 2)
        
        if item:
            symbol = self.item_symbols.get(item.item_type, "?")
            text = self.font.render(symbol, True, self.quality_colors[item.quality])
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
            
            if item == self.selected_item:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, 3)

    def draw_exp_info(self, player: Player, x: int, y: int):
        level_text = self.font.render(f"Level {player.level}", True, GameConfig.WHITE)
        self.screen.blit(level_text, (x, y))
        
        exp_text = self.small_font.render(
            f"EXP: {player.experience}/{player.next_level_exp}", 
            True, GameConfig.WHITE
        )
        self.screen.blit(exp_text, (x, y + 30))
        
        bar_width = 150
        bar_height = 10
        progress = player.experience / player.next_level_exp
        
        pygame.draw.rect(self.screen, (50, 50, 50), (x, y + 50, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (x, y + 50, int(bar_width * progress), bar_height))

    def draw_stats(self, player: Player):
        x = self.window_x + 20
        y = self.window_y + 50
        stats = player.get_total_stats()
        
        self.draw_exp_info(player, x, y)
        y += 80
        
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
        mp_percent = 1.0
        pygame.draw.rect(self.screen, (0, 0, 50), (x, y, bar_width, bar_height))
        pygame.draw.rect(self.screen, (0, 0, 200), (x, y, int(bar_width * mp_percent), bar_height))
        mp_text = self.font.render(f"MP: 100/100", True, GameConfig.WHITE)
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
            if len(row) < 3:
                text = self.font.render(f"    {line_text}", True, GameConfig.WHITE)
            else:
                text = self.font.render(line_text, True, GameConfig.WHITE)
            self.screen.blit(text, (x, y))
            y += 25

    def draw_item_info(self):
        if not self.hovered_item:
            return

        mouse_x, mouse_y = pygame.mouse.get_pos()
        padding = 10
        line_height = 25
        
        lines = [
            self.hovered_item.full_name,
            f"Type: {self.hovered_item.item_type.name}"
        ]
        
        for stat_name, value in self.hovered_item.stats.__dict__.items():
            if value > 0:
                lines.append(f"{stat_name.replace('_', ' ').title()}: +{value}")
            
        max_width = max(self.font.size(line)[0] for line in lines)
        height = len(lines) * line_height + padding * 2
        
        info_x = min(mouse_x + 20, self.screen.get_width() - max_width - padding)
        info_y = min(mouse_y, self.screen.get_height() - height - padding)
        
        info_rect = pygame.Rect(info_x, info_y, max_width + padding * 2, height)
        pygame.draw.rect(self.screen, (0, 0, 0), info_rect)
        pygame.draw.rect(self.screen, GameConfig.WHITE, info_rect, 1)
        
        for i, line in enumerate(lines):
            text = self.font.render(line, True, GameConfig.WHITE)
            self.screen.blit(text, (info_x + padding, info_y + padding + i * line_height))

    def render(self, player):
            if not self.visible:
                return
            
            window_rect = pygame.Rect(self.window_x, self.window_y, self.window_width, self.window_height)
            pygame.draw.rect(self.screen, (0, 0, 0), window_rect)
            pygame.draw.rect(self.screen, GameConfig.WHITE, window_rect, 2)
        
            # Draw title
            title = self.font.render("Inventory", True, GameConfig.WHITE)
            title_rect = title.get_rect(centerx=self.window_x + self.window_width//2, y=self.window_y + 10)
            self.screen.blit(title, title_rect)
        
            # Draw stats
            self.draw_stats(player)
        
            # Draw equipment slots
            for slot_type, rect in self.equipment_slots.items():
                item = player.inventory.equipped.get(slot_type)
                self.draw_item(item, rect)
            
            # Draw ring slots
            for i, rect in enumerate(self.ring_slots):
                item = player.inventory.rings[i] if i < len(player.inventory.rings) else None
                self.draw_item(item, rect)
            
            # Draw inventory grid
            for i, rect in enumerate(self.inventory_slots):
                item = player.inventory.items[i] if i < len(player.inventory.items) else None
                self.draw_item(item, rect)
            
            if self.hovered_item:
                self.draw_item_info()
            
            if self.dragging and self.selected_item:
                mouse_pos = pygame.mouse.get_pos()
                drag_rect = pygame.Rect(
                    mouse_pos[0] - self.slot_size // 2,
                    mouse_pos[1] - self.slot_size // 2,
                    self.slot_size,
                    self.slot_size
                )
                self.draw_item(self.selected_item, drag_rect)

    def handle_click(self, player: Player, pos: Tuple[int, int], is_down: bool) -> bool:
        if not self.visible:
            return False

        print(f"\n=== Handling Inventory Click ===")
        print(f"{'Mouse down' if is_down else 'Mouse up'} at {pos}")
        print(f"Current state: dragging={self.dragging}, selected_item={self.selected_item.name if self.selected_item else None}")

        if is_down:
            print("Processing mouse down...")
            if not self.dragging:  # Only select item if not already dragging
                self.dragging = True
                self.drag_start_pos = pos
                # Check equipment slots first
                for slot_type, rect in self.equipment_slots.items():
                    if rect.collidepoint(pos):
                        self.selected_item = player.inventory.equipped.get(slot_type)
                        return True

                # Then check ring slots
                for i, rect in enumerate(self.ring_slots):
                    if rect.collidepoint(pos):
                        self.selected_item = player.inventory.rings[i]
                        return True

                # Finally check inventory slots
                for i, rect in enumerate(self.inventory_slots):
                    if rect.collidepoint(pos) and i < len(player.inventory.items):
                        self.selected_item = player.inventory.items[i]
                        print(f"Selected inventory item: {self.selected_item.name}")
                        return True
        else:  # Mouse up
            print("Processing mouse up...")
            if self.dragging and self.selected_item:
                print(f"Attempting to drop {self.selected_item.name}")
            
                # Check if dropping outside inventory window
                if (pos[0] < self.window_x or pos[0] > self.window_x + self.window_width or
                    pos[1] < self.window_y or pos[1] > self.window_y + self.window_height):
                    print("Dropping outside inventory - selling item")
                    self.sell_item(player, self.selected_item)
                else:
                    # Check equipment slots
                    for slot_type, rect in self.equipment_slots.items():
                        if rect.collidepoint(pos):
                            print(f"Dropping on equipment slot {slot_type.name}")
                            if self.selected_item.item_type == slot_type:
                                self.equip_item(player, slot_type)
                                break

                    # Check ring slots
                    for i, rect in enumerate(self.ring_slots):
                        if rect.collidepoint(pos):
                            print(f"Dropping on ring slot {i}")
                            if self.selected_item.item_type == ItemType.RING:
                                self.equip_ring(player, i)
                                break

            self.dragging = False
            self.selected_item = None
            return True

        return False

    def handle_hover(self, player: Player, pos: Tuple[int, int]):
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
            if rect.collidepoint(pos) and i < len(player.inventory.rings):
                self.hovered_item = player.inventory.rings[i]
                return

        # Check inventory slots
        for i, rect in enumerate(self.inventory_slots):
            if rect.collidepoint(pos) and i < len(player.inventory.items):
                self.hovered_item = player.inventory.items[i]
                return

    def equip_item(self, player: Player, slot_type: ItemType) -> None:
        print(f"Attempting to equip {self.selected_item.name} to {slot_type.name}")
        if self.selected_item and self.selected_item.item_type == slot_type:
            # Remove from current equipped slot if something is there
            old_item = player.inventory.equipped.get(slot_type)
            if old_item:
                print(f"Unequipping {old_item.name}")
                player.inventory.items.append(old_item)
        
            # Remove from inventory and equip
            player.inventory.items.remove(self.selected_item)
            player.inventory.equipped[slot_type] = self.selected_item
            print(f"Equipped {self.selected_item.name}")
        
            if self.combat_log:
                self.combat_log.add_message(f"Equipped {self.selected_item.name}")

    def equip_ring(self, player: Player, slot: int) -> None:
        print(f"Attempting to equip ring {self.selected_item.name} to slot {slot}")
        if self.selected_item and self.selected_item.item_type == ItemType.RING:
            # Remove from current ring slot if something is there
            old_item = player.inventory.rings[slot]
            if old_item:
                print(f"Unequipping ring {old_item.name}")
                player.inventory.items.append(old_item)
        
            # Remove from inventory and equip
            player.inventory.items.remove(self.selected_item)
            player.inventory.rings[slot] = self.selected_item
            print(f"Equipped ring {self.selected_item.name}")
        
            if self.combat_log:
                self.combat_log.add_message(f"Equipped {self.selected_item.name}")

    def sell_item(self, player: Player, item: Item) -> None:
        print(f"Attempting to sell {item.name}")
        sell_value = (item.quality + 1) * 10 + RandomUtils.int(5, 15)
        player.inventory.gold += sell_value
    
        # Remove from inventory
        if item in player.inventory.items:
            player.inventory.items.remove(item)
        
        print(f"Sold {item.name} for {sell_value} gold")
        if self.combat_log:
            self.combat_log.add_message(f"Sold {item.name} for {sell_value} gold")