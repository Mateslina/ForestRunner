"""
UI helpers shared across screens.

Contains:
- shared colors
- button drawing + button group layout/helpers
- top-right icon + amount helpers (coin counter)
"""

from dataclasses import dataclass
from typing import Mapping, Optional

import pygame as pg

from main.core.game_state import GameState

# ---------------- shared colors ----------------

WHITE: tuple[int, int, int] = (255, 255, 255)
YELLOW: tuple[int, int, int] = (255, 215, 80)

# ---------------- button drawing ----------------


@dataclass(frozen=True)
class ButtonStyle:
    """Visual parameters for drawing a button."""

    radius: int = 14
    fill: tuple[int, int, int] = (60, 60, 60)
    fill_hover: tuple[int, int, int] = (90, 90, 90)
    border: tuple[int, int, int] = (210, 210, 210)
    border_width: int = 2
    text_color: tuple[int, int, int] = WHITE


DEFAULT_BUTTON_STYLE = ButtonStyle()


# @generated [all] ChatGPT : make the button drawing reusable so i dont have to reapet this everywhere ...
def make_button_drawer(
    win: pg.Surface,
    font: pg.font.Font,
    style: ButtonStyle = DEFAULT_BUTTON_STYLE,
):
    """
    Create a button drawing function bound to (win, font, style).

    Returned function signature: draw(rect, text, hovered) -> None
    """

    def _draw(rect: pg.Rect, text: str, hovered: bool) -> None:
        bg = style.fill_hover if hovered else style.fill
        pg.draw.rect(win, bg, rect, border_radius=style.radius)
        pg.draw.rect(
            win,
            style.border,
            rect,
            width=style.border_width,
            border_radius=style.radius,
        )

        label = font.render(text, True, style.text_color)
        win.blit(
            label,
            (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2,
            ),
        )

    return _draw


# ---------------- button groups ----------------

def layout_button_group(w: int, h: int, keys: list[GameState]) -> dict[GameState, pg.Rect]:
    """Creates layout stack for buttons and returns them in {Gamestate: Rect} dict."""
    x = w // 2 - 240 // 2
    start_y = int(h * 0.6)

    rects: dict[GameState, pg.Rect] = {}
    for i, key in enumerate(keys):
        y = start_y + i * (60 + 16)
        rects[key] = pg.Rect(x, y, 240, 60)
    return rects


def draw_button_group(
    win: pg.Surface,
    font: pg.font.Font,
    buttons: Mapping[GameState, pg.Rect],
    labels: Mapping[GameState, str],
    style: ButtonStyle = DEFAULT_BUTTON_STYLE,
) -> None:
    """Draw all buttons in a group."""
    if not buttons:
        return

    mx, my = pg.mouse.get_pos()
    mouse = (mx, my)

    draw_btn = make_button_drawer(win, font, style=style)
    for key, rect in buttons.items():
        draw_btn(rect, labels[key], hovered=rect.collidepoint(mouse))


def clicked_button(event, buttons: Mapping[GameState, pg.Rect]) -> Optional[GameState]:
    """Return key if left-click hits a button, else None."""
    if (
        event.type != pg.MOUSEBUTTONDOWN or event.button != 1  # pylint: disable=no-member
    ):
        return None

    for key, rect in buttons.items():
        if rect.collidepoint(event.pos):
            return key
    return None


# ---------------- top-right icon + amount ----------------

def draw_top_right_icon_amount(
    win: pg.Surface,
    window_w: int,
    icon: pg.Surface,
    amount_surf: pg.Surface,
) -> None:
    """Draw an icon + amount text group aligned to the top-right."""
    top_y = 12
    amount_x_offset = -10

    cw, ch = icon.get_size()

    extra = -amount_x_offset if amount_x_offset < 0 else amount_x_offset
    group_w = cw + extra + amount_surf.get_width()
    group_h = max(ch, amount_surf.get_height())

    icon_x = window_w - 20 - group_w
    icon_y = top_y + group_h // 2 - ch // 2

    win.blit(icon, (icon_x, icon_y))

    amount_x = icon_x + cw + amount_x_offset
    amount_y = top_y + group_h // 2 - amount_surf.get_height() // 2 + 2
    win.blit(amount_surf, (amount_x, amount_y))


# ---------------- coin counter (top-right) ----------------

_COIN_SCALE = 0.7
_COIN_FONT = 58


# @generated [all] ChatGPT : center the coins ammount with the icon on the top right corner and make it reusable between different screens
def draw_bank_coins_top_right(
    win: pg.Surface,
    window_w: int,
    coins_bank: int,
    base_coin: pg.Surface,
    cache: dict,
) -> None:
    """Draw bank coin counter (icon + amount) aligned to top-right."""
    size = (
        int(base_coin.get_width() * _COIN_SCALE),
        int(base_coin.get_height() * _COIN_SCALE),
    )

    coin_sprite = cache.get("coin_sprite")
    if coin_sprite is None or cache.get("coin_size") != size:
        cache["coin_size"] = size
        cache["coin_sprite"] = pg.transform.smoothscale(base_coin, size)
        coin_sprite = cache["coin_sprite"]

    amount_font = cache.get("amount_font")
    if amount_font is None:
        cache["amount_font"] = pg.font.SysFont(None, _COIN_FONT, bold=True)
        amount_font = cache["amount_font"]

    amount_surf = amount_font.render(str(coins_bank), True, YELLOW)
    draw_top_right_icon_amount(win, window_w, coin_sprite, amount_surf)
