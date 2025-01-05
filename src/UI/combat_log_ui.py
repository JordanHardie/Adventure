from ..config.game_config import GameConfig
from typing import List, Optional, Dict
from ..engine.player import Item

class CombatLogUI:
    """Displays combat and loot messages during gameplay."""

    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.messages: List[str] = []
        self.max_messages = 5
        self.visible = True
        self.fade_timers: Dict[int, int] = {}  # Message index -> frames remaining
        self.fade_duration = 180  # 3 seconds at 60 FPS

    def add_message(self, message: str):
        """Add a message to the combat log."""
        self.messages.append(message)
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
            self.fade_timers = {k-1: v for k, v in self.fade_timers.items() if k > 0}
        self.fade_timers[len(self.messages) - 1] = self.fade_duration

    def add_loot_message(self, items: Optional[List[Item]], gold: int):
        """Create formatted message for loot drops."""
        if not items and gold <= 0:
            return
            
        parts = []
        if gold > 0:
            parts.append(f"{gold} gold")
            
        if items:
            item_names = [f"{item.full_name}" for item in items]
            if len(items) == 1:
                parts.append(item_names[0])
            else:
                parts[-1] = f"{', '.join(item_names[:-1])} and {item_names[-1]}"
                
        loot_msg = f"Obtained: {' '.join(parts)}"
        self.add_message(loot_msg)

    def update(self):
        """Update fade timers for messages."""
        to_remove = []
        for idx, timer in self.fade_timers.items():
            self.fade_timers[idx] = max(0, timer - 1)
            if self.fade_timers[idx] == 0:
                to_remove.append(idx)
                
        for idx in sorted(to_remove, reverse=True):
            del self.fade_timers[idx]
            del self.messages[idx]

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