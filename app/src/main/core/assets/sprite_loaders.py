"""
Sprite-loading and sprite-building helpers.

Loads and scales game sprites (player, coins, obstacles, power-ups, UI).
"""

import pygame as pg

from main.core.assets.assets_loader import load_image
from main.core.assets.models import PlayerSprites, CoinSprites

COIN_SIZE_PX = 96
POWERUP_TO_COIN = 0.75


def _scale_to(s: pg.Surface, w: int, h: int) -> pg.Surface:
    """Return ``s`` scaled to (w, h), clamping dimensions to at least 1px."""
    return pg.transform.scale(s, (max(1, int(w)), max(1, int(h))))


def _scale_to_powerup_size(s: pg.Surface) -> pg.Surface:
    """Return ``s`` scaled to the standard power-up size (relative to coin size)."""
    size = int(COIN_SIZE_PX * POWERUP_TO_COIN)
    return pg.transform.smoothscale(s, (size, size))


def load_coin_sprites(coin_base: pg.Surface) -> CoinSprites:
    """Build and return coin sprites (normal + double) from the tileset base coin."""
    cw = int(coin_base.get_width() * 3.0)
    ch = int(coin_base.get_height() * 3.0)
    normal = pg.transform.smoothscale(coin_base, (cw, ch))

    base_double = load_image("collectibles/double_coin.png")
    double = pg.transform.smoothscale(base_double, (int(cw * 1.5), ch))

    return CoinSprites(normal=normal, double=double)


def load_bird_frames() -> list[pg.Surface]:
    """Load, split, flip and scale the two bird animation frames."""
    bird_sheet = load_image("obstacles/bird.png")
    bw = bird_sheet.get_width() // 2
    bh = bird_sheet.get_height()

    frame_trim = 115
    scale = 0.15

    f0 = bird_sheet.subsurface(pg.Rect(0, 0, bw - frame_trim, bh))
    f1 = bird_sheet.subsurface(pg.Rect(bw + frame_trim, 0, bw - frame_trim, bh))

    f0 = pg.transform.flip(f0, True, False)
    f1 = pg.transform.flip(f1, True, False)

    f0 = _scale_to(f0, int(bw * scale), int(bh * scale))
    f1 = _scale_to(f1, int(bw * scale), int(bh * scale))

    return [f0, f1]


def load_player_frames() -> PlayerSprites:
    """Load and scale player run/crouch frames and return them grouped."""
    run1 = load_image("player/run1.png")
    run2 = load_image("player/run2.png")
    crouch1 = load_image("player/crouch1.png")
    crouch2 = load_image("player/crouch2.png")

    div = 3
    rw, rh = run1.get_size()
    run_w = max(1, int(rw / div))
    run_h = max(1, int(rh / div))

    run1 = _scale_to(run1, run_w, run_h)
    run2 = _scale_to(run2, run_w, run_h)

    crouch_h = int(run_h * 0.6)
    crouch1 = _scale_to(crouch1, run_w, crouch_h)
    crouch2 = _scale_to(crouch2, run_w, crouch_h)

    return PlayerSprites(
        run_frames=[run1, run2],
        crouch_frames=[crouch1, crouch2],
        stand_size=run1.get_size(),
        crouch_size=crouch1.get_size(),
    )


def load_powerups(extra_life_sprite: pg.Surface) -> dict[str, pg.Surface]:
    """Load and return power-up sprites, scaled to the standard power-up size."""
    return {
        "shield": _scale_to_powerup_size(load_image("collectibles/shield.png")),
        "double_coins": _scale_to_powerup_size(
            load_image("collectibles/double_coins.png")
        ),
        "double_score": _scale_to_powerup_size(
            load_image("collectibles/double_score.png")
        ),
        "extra_life": _scale_to_powerup_size(extra_life_sprite),
    }


def load_shop_background() -> pg.Surface:
    """Load the shop background sprite."""
    return load_image("background/shop-16by9.png")


def load_title_sign() -> pg.Surface:
    """Load and scale the title sign sprite."""
    base = load_image("background/sign.png")
    sign_scale = 0.5
    lw = int(base.get_width() * sign_scale)
    lh = int(base.get_height() * sign_scale)
    return pg.transform.smoothscale(base, (lw, lh))
