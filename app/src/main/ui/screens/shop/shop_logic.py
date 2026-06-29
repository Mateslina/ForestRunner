"""
Shop upgrade logic.

Handles upgrade levels, pricing, affordability checks, and purchases.
"""
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ShopItem:
    """Represents one shop item."""
    key: str
    kind: str
    name: str
    max_level: int
    base_cost: int
    cost_step: int


DEFAULT_SHOP_ITEMS: tuple[ShopItem, ...] = (
    ShopItem(
        key="shield_duration_level",
        kind="shield",
        name="Shield",
        max_level=5,
        base_cost=30,
        cost_step=25,
    ),
    ShopItem(
        key="double_coins_duration_level",
        kind="double_coins",
        name="x2 Coins",
        max_level=5,
        base_cost=40,
        cost_step=30,
    ),
    ShopItem(
        key="double_score_duration_level",
        kind="double_score",
        name="x2 Score",
        max_level=5,
        base_cost=40,
        cost_step=30,
    ),
    ShopItem(
        key="max_lives_level",
        kind="extra_life",
        name="Lives",
        max_level=2,
        base_cost=80,
        cost_step=80,
    ),
)


class ShopLogic:
    """Upgrade costs/levels/purchases for the shop screen."""

    def __init__(self, progress, items: Iterable[ShopItem]) -> None:
        self._progress = progress
        self.items = list(items)

    def level(self, key: str) -> int:
        """Return current upgrade level for key."""
        return int(self._progress.upgrades.get(key, 0))

    def cost(self, item: ShopItem) -> int:
        """Return current purchase cost for item at its current level."""
        lvl = self.level(item.key)
        return item.base_cost + item.cost_step * lvl

    def can_buy(self, item: ShopItem) -> bool:
        """Return True if item is not maxed and player has enough coins."""
        lvl = self.level(item.key)
        return lvl < item.max_level and self._progress.coins_bank >= self.cost(item)

    def buy(self, item: ShopItem) -> bool:
        """Attempt to buy item. Returns True if purchase succeeded."""
        if not self.can_buy(item):
            return False
        cost = self.cost(item)
        self._progress.coins_bank -= cost
        self._progress.upgrades[item.key] = self.level(item.key) + 1
        return True
