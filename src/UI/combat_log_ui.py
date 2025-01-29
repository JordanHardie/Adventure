from ..engine.player import Item
from typing import List, Optional
from ..engine.generics import BaseUI
from ..config.game_config import GameConfig

class CombatLogUI(BaseUI):
    def __init__(self, screen, font):
        super().__init__(screen)
        self.font = font
        self.messages = []
        self.max_messages = 5
        self.fade_timers = {}  # Message index -> frames remaining
        self.fade_duration = 180
        self.visible = True

    def add_message(self, message: str):
        """Add a message to the combat log."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            self.fade_timers = {k-1: v for k, v in self.fade_timers.items() if k > 0}
        self.fade_timers[len(self.messages) - 1] = self.fade_duration

    def add_loot_message(self, items: Optional[List[Item]], gold: int):
        print("\n=== Adding Loot Message ===")
        print(f"Items: {[item.name for item in items] if items else 'None'}")
        print(f"Gold: {gold}")
    
        if not items and gold <= 0:
            print("No loot to display")
            return
        
        parts = []
        if gold > 0:
            parts.append(f"{gold} gold")
        
        if items:
            item_names = [f"{item.name} ({item.item_type.name})" for item in items]
            if len(items) == 1:
                parts.append(item_names[0])
            else:
                parts[-1] = f"{', '.join(item_names[:-1])} and {item_names[-1]}"
            
        loot_msg = f"Obtained: {' '.join(parts)}"
        print(f"Final message: {loot_msg}")
        self.add_message(loot_msg)

    def update(self):
        """Update fade timers for messages."""
        to_remove = []
        for idx, timer in self.fade_timers.items():
            self.fade_timers[idx] = max(0, timer - 1)
            if self.fade_timers[idx] == 0:
                to_remove.append(idx)
            
        if to_remove:
            # Remove messages and timers starting from highest index
            for idx in sorted(to_remove, reverse=True):
                if idx < len(self.messages):  # Check if index exists
                    del self.messages[idx]
                del self.fade_timers[idx]

    def draw(self):
        """Render combat log messages with fade effect."""
        if not self.visible or not self.messages:
            return
            
        self.update()
        y_offset = self.screen.get_height() - (self.max_messages * 25 + 10)
        
        for i, message in enumerate(self.messages):
            alpha = 255
            if i in self.fade_timers:
                alpha = int((self.fade_timers[i] / self.fade_duration) * 255)
            
            text = self.font.render(message, True, GameConfig.WHITE)
            text.set_alpha(alpha)
            self.screen.blit(text, (10, y_offset + i * 25))

    def render(self):
        if not self.visible or not self.messages:
            return
            
        self.update()
        y_offset = self.screen.get_height() - (self.max_messages * 25 + 10)
        
        for i, message in enumerate(self.messages):
            alpha = 255
            if i in self.fade_timers:
                alpha = int((self.fade_timers[i] / self.fade_duration) * 255)
            
            text = self.font.render(message, True, GameConfig.WHITE)
            text.set_alpha(alpha)
            self.screen.blit(text, (10, y_offset + i * 25))