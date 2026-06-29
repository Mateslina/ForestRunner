"""
Heads-up display (HUD).

Renders score, coin counter, and player lives (hearts).
"""

from dataclasses import dataclass

import pygame as pg

from main.ui.ui_helpers import draw_bank_coins_top_right, WHITE, YELLOW


@dataclass(frozen=True)
class HudState:
    """Current values to render on the HUD."""
    score: int
    collected_coins: int
    lives: int
    max_lives: int
    double_score_time: float


class HUD:  # pylint: disable=too-few-public-methods
    """HUD renderer for score, coins and lives."""

    PADDING = 14
    ICON_SIZE = 48

    def __init__(self, font_small, font_big, assets):
        self.font_small = font_small
        self.font_big = font_big
        self.assets = assets
        self._heart_full, self._heart_empty = self._build_hearts()
        self._coin_ui_cache: dict = {}

    def _build_hearts(self) -> tuple[pg.Surface, pg.Surface]:
        heart_base = self.assets.collectibles.powerups.all["extra_life"]
        heart_full = pg.transform.smoothscale(heart_base, (self.ICON_SIZE, self.ICON_SIZE))
        heart_empty = heart_full.copy()
        heart_empty.set_alpha(60)
        return heart_full, heart_empty

    def _score_color(self, double_score_time: float) -> tuple[int, int, int]:
        # flicker the color when double score is ending
        if double_score_time <= 0.0:
            return WHITE

        if double_score_time <= 1.0:
            t = pg.time.get_ticks()
            # blink every 100ms
            return YELLOW if int(t // 100) % 2 == 0 else WHITE

        return YELLOW

    def draw(self, window: pg.Surface, state: HudState) -> None:
        """Render HUD elements based on the provided state."""
        w, _ = window.get_size()

        draw_bank_coins_top_right(
            win=window,
            window_w=w,
            coins_bank=state.collected_coins,
            base_coin=self.assets.collectibles.coins.normal,
            cache=self._coin_ui_cache,
        )

        score_color = self._score_color(state.double_score_time)
        score_surf = self.font_big.render(f"Score: {state.score}", True, score_color)
        window.blit(score_surf, (w // 2 - score_surf.get_width() // 2, self.PADDING))

        x = self.PADDING
        y = self.PADDING
        step = self.ICON_SIZE + 6
        for i in range(state.max_lives):
            icon = self._heart_full if i < state.lives else self._heart_empty
            window.blit(icon, (x + i * step, y))
