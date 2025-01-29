"""
Core utilities and services for the Adventure game.
Provides error handling, logging, configuration management, and common services.
"""

import os
import logging
import functools
from typing import Any, Callable, Dict, Optional, TypeVar

from src.combat.entity import Entity
from src.combat.skills import Skill
from src.engine.player import ItemType, Item, Player

# Type variables for generic function decorators
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

class GameLogger:
    """Centralized logging system for the game."""

    def __init__(self, debug_mode: bool = False):
        self.logger = logging.getLogger('adventure')
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

        # Console handler
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console)

        # File handler
        log_dir = os.path.join(os.getenv('APPDATA'), 'Adventure', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, 'game.log')
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)

    def debug(self, msg: str):
        self.logger.debug(msg)

    def info(self, msg: str):
        self.logger.info(msg)

    def warning(self, msg: str):
        self.logger.warning(msg)

    def error(self, msg: str):
        self.logger.error(msg)


class ConfigService:
    """Centralized configuration management."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.debug_mode = bool(os.getenv('ADVENTURE_DEBUG', False))
            self.logger = GameLogger(self.debug_mode)
            self._cache: Dict[str, Any] = {}

    def get_config(self, name: str) -> Optional[Dict]:
        """Get configuration data, using cache if available."""
        if name in self._cache:
            return self._cache[name]

        try:
            from ..generics import load_json_config
            config = load_json_config(f"{name}.json")
            self._cache[name] = config
            return config
        except Exception as e:
            self.logger.error(f"Error loading config {name}: {str(e)}")
            return None


def with_error_handling(func: F) -> F:
    """Decorator to add error handling and logging to functions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        config = ConfigService()
        try:
            return func(*args, **kwargs)
        except Exception as e:
            config.logger.error(
                f"Error in {func.__name__}: {str(e)}"
            )
            raise

    return wrapper


class CombatService:
    """Service layer for complex combat operations."""

    def __init__(self):
        self.config = ConfigService()
        self.logger = self.config.logger

    @with_error_handling
    def calculate_damage(self, attacker: 'Entity', defender: 'Entity',
                         skill: Optional['Skill'] = None) -> Dict[str, Any]:
        """Calculate combat damage with optional skill modifiers."""
        from ..generics import RandomUtils

        # Base damage calculation
        if skill and skill.skill_type == "MAGICAL":
            attack = attacker.current_stats.magic_power
            defence = defender.current_stats.magic_defence
        else:
            attack = attacker.current_stats.strength
            defence = defender.current_stats.defence

        # Calculate base damage
        base_damage = max(1, attack - defence // 2)

        # Apply skill modifiers if present
        if skill:
            base_damage = self._apply_skill_modifiers(
                base_damage, attacker, skill
            )

        # Critical hit calculation
        crit_chance = attacker.current_stats.dexterity * 0.05
        is_crit = RandomUtils.chance(crit_chance)

        if is_crit:
            base_damage *= 2

        return {
            "damage": base_damage,
            "is_critical": is_crit,
            "attack_type": "magical" if skill and skill.skill_type == "MAGICAL" else "physical"
        }

    @staticmethod
    def _apply_skill_modifiers(base_damage: int, attacker: 'Entity',
                               skill: 'Skill') -> int:
        """Apply skill-specific damage modifiers."""
        if not skill.scaling:
            return base_damage

        modifier = 1.0
        for stat, scale in skill.scaling.items():
            stat_value = getattr(attacker.current_stats, stat, 0)
            modifier += (stat_value * scale)

        return int(base_damage * modifier)


class InventoryService:
    """Service layer for inventory management."""

    def __init__(self):
        self.config = ConfigService()
        self.logger = self.config.logger

    @with_error_handling
    def can_equip_item(self, player: 'Player', item: 'Item',
                       slot: Optional[int] = None) -> bool:
        """Check if an item can be equipped."""
        if item.item_type not in player.inventory.equipped:
            if item.item_type != ItemType.RING:
                return False

            if slot is None or slot >= len(player.inventory.rings):
                return False

        return True

    @with_error_handling
    def calculate_stats_change(self, item: 'Item',
                               unequip: bool = False) -> Dict[str, int]:
        """Calculate stat changes from equipping/unequipping an item."""
        changes = {}
        multiplier = -1 if unequip else 1

        for stat_name, value in item.stats.__dict__.items():
            if value != 0:
                changes[stat_name] = value * multiplier

        return changes