"""
Playing controller.

Owns the run state + gameplay orchestration (difficulty, buffs, collisions, revive, finish).
"""

from dataclasses import dataclass, field

from main.core.constants import GROUND_Y, BASE_SPEED
from main.core.game_state import GameState
from main.entities.player.player import Player
from main.entities.obstacles.obstacle_manager import ObstacleManager
from main.entities.collectibles.collectible_manager import CollectibleManager


@dataclass
class BuffState:
    """Timed multipliers and their remaining durations."""

    score_mult: float = 1.0
    double_score_time: float = 0.0
    coins_mult: int = 1
    double_coins_time: float = 0.0


@dataclass
class RunState:
    """Mutable state of the current game run."""

    score: float = 0.0
    collected_coins: int = 0
    buffs: BuffState = field(default_factory=BuffState)
    max_lives: int = 3
    lives: int = 3


class PlayingController:
    """Gameplay orchestration for PlayingScreen."""

    # revive / death
    REVIVE_INVULNERABLE_TIME = 1.2
    FALL_DEATH_MARGIN = 10

    # difficulty scaling
    SPEED_PER_SCORE = 0.01
    MAX_GAME_SPEED_MULT = 1.5

    OBSTACLE_CHANCE_BASE = 0.4
    OBSTACLE_CHANCE_PER_SCORE = 0.002
    MAX_OBSTACLE_CHANCE = 0.5

    # power-up durations
    SHIELD_BASE_DURATION = 3.0
    SHIELD_PER_LEVEL = 1.5

    DOUBLE_SCORE_BASE_DURATION = 6.0
    DOUBLE_SCORE_PER_LEVEL = 2.0

    DOUBLE_COINS_BASE_DURATION = 8.0
    DOUBLE_COINS_PER_LEVEL = 2.0

    def __init__(self, game) -> None:
        self.game = game

        # reset entities for a new run
        self.game.ctx.player = Player(self.game.ctx.assets)
        self.game.ctx.ground.reset(BASE_SPEED)

        # systems owned by controller
        self.obstacles = ObstacleManager(self.game.ctx.assets)
        self.collectibles = CollectibleManager(assets=self.game.ctx.assets)

        # run state
        lvl = self.game.ctx.progress.upgrades.get("max_lives_level", 0)
        max_lives = 3 + int(lvl)
        self.run = RunState(max_lives=max_lives, lives=max_lives)

    @property
    def display_score(self) -> int:
        """Score shown to the player."""
        return int(self.run.score)

    # ---------- input API (called by screen) ----------

    def on_jump(self) -> None:
        """Trigger a player jump action."""
        self.game.ctx.player.jump()

    def set_crouch(self, crouch: bool) -> None:
        """Enable or disable player crouching."""
        self.game.ctx.player.set_crouch(crouch)

    # ---------- main loop API ----------

    def update(self, dt: float) -> None:
        """Advance gameplay by dt seconds."""
        self.game.ctx.player.update(
            dt, self.game.ctx.ground, speed=self.game.ctx.ground.speed
        )

        self._update_buffs(dt)
        self._update_score(dt)
        self._update_difficulty()

        self.game.ctx.background.update(dt, self.game.ctx.ground.speed)

        self._update_world(dt)
        self._check_end_conditions()

    # ---------- internals ----------

    def _update_score(self, dt: float) -> None:
        self.run.score += dt * self.run.buffs.score_mult

    def _update_buffs(self, dt: float) -> None:
        buffs = self.run.buffs

        if buffs.double_score_time > 0.0:
            buffs.double_score_time -= dt
            if buffs.double_score_time <= 0.0:
                buffs.double_score_time = 0.0
                buffs.score_mult = 1.0

        if buffs.double_coins_time > 0.0:
            buffs.double_coins_time -= dt
            if buffs.double_coins_time <= 0.0:
                buffs.double_coins_time = 0.0
                buffs.coins_mult = 1
                self.collectibles.set_coin_sprite(
                    self.game.ctx.assets.collectibles.coins.normal
                )

    def _revive(self) -> None:
        self.game.ctx.player.respawn()
        self.game.ctx.player.set_invulnerable(self.REVIVE_INVULNERABLE_TIME)

        # keep only obstacles that are away from the player
        self.obstacles.obstacles = [
            o
            for o in self.obstacles.obstacles
            if not o.rect.colliderect(self.game.ctx.player.rect.inflate(30, 30))
        ]

    def _update_difficulty(self) -> None:
        """Makes the ground move faster and obstacles more frequent."""
        score_display = self.display_score

        speed_factor = 1.0 + min(
            score_display * self.SPEED_PER_SCORE, self.MAX_GAME_SPEED_MULT
        )
        self.game.ctx.ground.speed = BASE_SPEED * speed_factor

        obstacle_chance = self.OBSTACLE_CHANCE_BASE + min(
            score_display * self.OBSTACLE_CHANCE_PER_SCORE, self.MAX_OBSTACLE_CHANCE
        )
        self.game.ctx.ground.obstacle_chance = obstacle_chance

    def _apply_powerups(self, powerups) -> None:
        """Apply collected power-ups to the current run/player."""
        upgrades = self.game.ctx.progress.upgrades
        buffs = self.run.buffs

        for p in powerups:
            if p.kind == "shield":
                lvl = upgrades.get("shield_duration_level", 0)
                duration = self.SHIELD_BASE_DURATION + lvl * self.SHIELD_PER_LEVEL
                self.game.ctx.player.give_shield(duration)

            elif p.kind == "double_score":
                buffs.score_mult = 2.0
                lvl = upgrades.get("double_score_duration_level", 0)
                duration = (
                    self.DOUBLE_SCORE_BASE_DURATION + lvl * self.DOUBLE_SCORE_PER_LEVEL
                )
                buffs.double_score_time = max(buffs.double_score_time, duration)

            elif p.kind == "double_coins":
                buffs.coins_mult = 2
                lvl = upgrades.get("double_coins_duration_level", 0)
                duration = (
                    self.DOUBLE_COINS_BASE_DURATION + lvl * self.DOUBLE_COINS_PER_LEVEL
                )
                buffs.double_coins_time = max(buffs.double_coins_time, duration)
                self.collectibles.set_coin_sprite(
                    self.game.ctx.assets.collectibles.coins.double
                )

            elif p.kind == "extra_life" and self.run.lives < self.run.max_lives:
                self.run.lives += 1

    def _update_world(self, dt: float) -> None:
        # spawn new obstacles
        obstacle_requests = self.game.ctx.ground.update(dt)
        for req in obstacle_requests:
            self.obstacles.spawn_obstacle_at(
                req.x, ground=self.game.ctx.ground, flying=req.flying
            )

        self.obstacles.update(dt, self.game.ctx.ground.speed)

        self.collectibles.update(
            dt,
            speed=self.game.ctx.ground.speed,
            ground=self.game.ctx.ground,
            obstacles=self.obstacles.obstacles,
        )

        coins_collected = self.collectibles.collect_coin_collisions(
            self.game.ctx.player.rect
        )
        self.run.collected_coins += coins_collected * self.run.buffs.coins_mult

        powerups = self.collectibles.collect_powerup_collisions(
            self.game.ctx.player.rect
        )
        self._apply_powerups(powerups)

    def _finish_run(self) -> None:
        """Finalize the run: update progress, store temp stats, go to Game Over."""
        run_score = self.display_score

        self.game.ctx.progress.high_score = max(
            self.game.ctx.progress.high_score, run_score
        )
        self.game.ctx.progress.coins_bank += self.run.collected_coins

        self.game.runtime.temp = {
            "final_score": run_score,
            "coins_collected": self.run.collected_coins,
        }
        self.game.set_screen(GameState.GAME_OVER)

    def _check_end_conditions(self) -> None:
        player = self.game.ctx.player

        if player.invulnerable:
            return

        died = False

        if not player.on_ground and (
            player.rect.bottom > GROUND_Y + self.FALL_DEATH_MARGIN
        ):
            died = True

        hit = self.obstacles.get_first_collision(player.rect)
        if hit is not None:
            if player.shield_active:
                player.consume_shield()
                if hit in self.obstacles.obstacles:
                    self.obstacles.obstacles.remove(hit)
            else:
                died = True

        if not died:
            return

        if self.run.lives > 1:
            self.run.lives -= 1
            self._revive()
            return

        self.run.lives = 0
        self._finish_run()
