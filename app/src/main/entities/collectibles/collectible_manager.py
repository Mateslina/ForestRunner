"""
Collectible manager.

Spawns, updates, draws and handles collisions for coins and power-ups.
"""

import random
from dataclasses import dataclass
from typing import Any

import pygame as pg

from main.entities.collectibles.coins import Coin
from main.entities.collectibles.powerups import PowerUp
from main.entities.collectibles.collectible_spawner import CollectibleSpawner


@dataclass(frozen=True)
class SpawnTiming:
    """Spawn timing configuration."""
    powerup_chance: float = 0.10
    min_interval: float = 1.6
    max_interval: float = 4.0


@dataclass
class CollectibleState:
    """Mutable collectible state."""
    coin_sprite_normal: pg.Surface
    coin_sprite_double: pg.Surface
    coin_sprite_current: pg.Surface
    time_to_next_spawn: float


@dataclass
class CollectibleLists:
    """Active collectibles on screen."""
    coins: list[Coin]
    powerups: list[PowerUp]


class CollectibleManager:
    """Manages coins and powerups."""

    def __init__(
        self,
        assets: Any,
        timing: SpawnTiming | None = None,
    ) -> None:
        self.rand = random.Random()
        self.spawner = CollectibleSpawner(self.rand)
        self.assets = assets
        self.timing = timing or SpawnTiming()

        self.state = CollectibleState(
            coin_sprite_normal=self.assets.collectibles.coins.normal,
            coin_sprite_double=self.assets.collectibles.coins.double,
            coin_sprite_current=self.assets.collectibles.coins.normal,
            time_to_next_spawn=self._next_time(),
        )
        self.items = CollectibleLists(coins=[], powerups=[])

    def set_coin_sprite(self, sprite: pg.Surface) -> None:
        """Change coin sprite and update all existing coins immediately."""
        self.state.coin_sprite_current = sprite
        w, h = sprite.get_size()

        for coin in self.items.coins:
            anchor = coin.rect.midbottom
            coin.sprite = sprite
            coin.rect.size = (w, h)
            coin.rect.midbottom = anchor  # so center doesn't change

    def reset(self) -> None:
        """Clear all collectibles and reset spawn timing."""
        self.items.coins.clear()
        self.items.powerups.clear()
        self.state.coin_sprite_current = self.state.coin_sprite_normal
        self.state.time_to_next_spawn = self._next_time()

    def update(self, dt: float, speed: float, ground: Any, obstacles: Any) -> None:
        """Update spawn timer, spawn new collectibles, move existing, and cull offscreen."""
        self.state.time_to_next_spawn -= dt
        self._try_spawn(ground, obstacles)
        self._move_all(dt, speed)
        self._remove_offscreen()

    def collect_coin_collisions(self, rect: pg.Rect) -> int:
        """Collect coins colliding with `rect` and return how many were collected."""
        collected = 0
        remaining: list[Coin] = []
        for coin in self.items.coins:
            if coin.rect.colliderect(rect):
                collected += 1
            else:
                remaining.append(coin)
        self.items.coins = remaining
        return collected

    def collect_powerup_collisions(self, rect: pg.Rect) -> list[PowerUp]:
        """Collect powerups colliding with `rect` and return collected objects."""
        collected: list[PowerUp] = []
        remaining: list[PowerUp] = []
        for pwr in self.items.powerups:
            if pwr.rect.colliderect(rect):
                collected.append(pwr)
            else:
                remaining.append(pwr)
        self.items.powerups = remaining
        return collected

    def draw(self, surface: pg.Surface) -> None:
        """Draw all collectibles."""
        for coin in self.items.coins:
            coin.draw(surface)
        for pwr in self.items.powerups:
            pwr.draw(surface)

    # ---------- internals ----------

    def _next_time(self) -> float:
        """Sample next spawn time based on timing config."""
        t = self.timing
        return self.rand.uniform(t.min_interval, t.max_interval)

    def _occupied(self, rect: pg.Rect) -> bool:
        """Checks if a space is already occupied by another collectible"""
        for coin in self.items.coins:
            if rect.colliderect(coin.rect):
                return True
        for pwr in self.items.powerups:
            if rect.colliderect(pwr.rect):
                return True
        return False

    def _pick_powerup_kind(self) -> str:
        r = self.rand.random()
        if r < 0.25:
            return "shield"
        if r < 0.5:
            return "double_score"
        if r < 0.75:
            return "double_coins"
        return "extra_life"

    def _get_powerup_sprite(self, kind: str) -> pg.Surface:
        return self.assets.collectibles.powerups.all[kind]

    def _try_spawn(self, ground: Any, obstacles: Any) -> None:
        """Spawn a coin or powerup if the timer elapsed."""
        if self.state.time_to_next_spawn > 0.0:
            return

        spawn_powerup = self.rand.random() < float(self.timing.powerup_chance)

        coin_w = float(self.state.coin_sprite_current.get_width())
        coin_h = float(self.state.coin_sprite_current.get_height())
        pt = self.spawner.pick_spawn_point(coin_w, coin_h, ground, obstacles)

        # no valid spawn point -> retry
        if pt is None:
            self.state.time_to_next_spawn = 0.5
            return

        if spawn_powerup:
            self._spawn_powerup_at_point(pt, coin_w, coin_h)
        else:
            self._spawn_coin_at_point(pt, coin_w, coin_h)

        self.state.time_to_next_spawn = self._next_time()

    def _spawn_powerup_at_point(self, pt: Any, coin_w: float, coin_h: float) -> None:
        kind = self._pick_powerup_kind()
        sprite = self._get_powerup_sprite(kind)

        pw = float(sprite.get_width())
        ph = float(sprite.get_height())

        x = pt.x + (coin_w - pw) * 0.5
        y = pt.y + (coin_h - ph) * 0.5
        rect = pg.Rect(round(x), round(y), round(pw), round(ph))

        if not self._occupied(rect):
            self.items.powerups.append(PowerUp(x, y, kind=kind, sprite=sprite))

    def _spawn_coin_at_point(self, pt: Any, coin_w: float, coin_h: float) -> None:
        rect = pg.Rect(round(pt.x), round(pt.y), round(coin_w), round(coin_h))
        if not self._occupied(rect):
            self.items.coins.append(Coin(pt.x, pt.y, sprite=self.state.coin_sprite_current))

    def _move_all(self, dt: float, speed: float) -> None:
        for coin in self.items.coins:
            coin.update(dt, speed)
        for pwr in self.items.powerups:
            pwr.update(dt, speed)

    def _remove_offscreen(self) -> None:
        self.items.coins = [c for c in self.items.coins if c.rect.right > 0]
        self.items.powerups = [p for p in self.items.powerups if p.rect.right > 0]
