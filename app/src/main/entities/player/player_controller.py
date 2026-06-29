"""
PlayerController.

Updates Player state: physics, ground collision, timers, and animation.
"""

from dataclasses import dataclass
from typing import Any

from main.core.constants import GRAVITY, GROUND_Y, BASE_SPEED, PLAYER_X


@dataclass
class PlayerController:
    """Encapsulates player update logic."""

    def update(self, player: Any, dt: float, ground: Any, speed: float) -> None:
        """
        Update player internal state.
        """
        self._apply_gravity(player, dt)
        self._resolve_ground_collision(player, ground)
        self._update_shield(player, dt)
        self._update_invuln(player, dt)
        self._update_animation(player, dt, speed)
        player.sync_rect()

    # ---------------- physics ----------------

    def _apply_gravity(self, player: Any, dt: float) -> None:
        player.motion.velocity += GRAVITY * dt
        player.geom.y += player.motion.velocity * dt

    def _resolve_ground_collision(self, player: Any, ground: Any) -> None:
        player_ground_y = GROUND_Y - player.geom.stand_h

        feet_margin = 2.0
        left_x = PLAYER_X + feet_margin
        right_x = PLAYER_X + player.geom.stand_w - feet_margin
        feet_width = right_x - left_x
        min_overlap = max(1.0, 0.2 * feet_width)

        if ground.is_solid_at_x(left_x, right_x, min_overlap):
            if player.geom.y >= player_ground_y:
                player.geom.y = player_ground_y  # clamp the player to the ground
                player.motion.velocity = 0.0
                player.motion.on_ground = True
            else:
                player.motion.on_ground = False  # jumping
        else:
            player.motion.on_ground = False  # falling into the gap

    # ---------------- buffs ----------------

    def _update_shield(self, player: Any, dt: float) -> None:
        if not player.buffs.shield_active:
            return
        player.buffs.shield_time = max(0.0, player.buffs.shield_time - dt)
        if player.buffs.shield_time <= 0.0:
            player.buffs.shield_active = False

    def _update_invuln(self, player: Any, dt: float) -> None:
        player.buffs.invuln_time = max(0.0, player.buffs.invuln_time - dt)

    # ---------------- animation ----------------

    def _update_animation(self, player: Any, dt: float, speed: float) -> None:
        if not player.motion.on_ground:
            player.anim.t = 0.0
            return

        factor = speed / BASE_SPEED
        frame_time = max(0.05, 0.14 / factor)

        player.anim.t += dt
        if player.anim.t >= frame_time:
            player.anim.t = 0.0  # reset
            if player.motion.crouching:
                player.anim.crouch_i = 1 - player.anim.crouch_i
            else:
                player.anim.run_i = 1 - player.anim.run_i
