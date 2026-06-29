# @generated [all] ChatGPT : generate tests based on class implementation
import pygame as pg
import pytest

from main.core.constants import WIDTH, HEIGHT, BASE_SPEED
from main.core.game import Game
from main.core.game_config import GameConfig, SaveConfig, PygameConfig, FactoryConfig
from main.core.game_state import GameState


# ------------------------ fakes / stubs ------------------------

class _FakeGround:
    def __init__(self):
        self.reset_calls: list[float] = []

    def reset(self, speed: float):
        self.reset_calls.append(float(speed))


class _FakeScreen:
    def __init__(self, game: Game):
        self.game = game
        self.handle_calls = 0
        self.update_calls: list[float] = []
        self.draw_calls = 0

    def handle_events(self, event):
        self.handle_calls += 1

    def update(self, dt: float):
        self.update_calls.append(float(dt))

    def draw(self):
        self.draw_calls += 1


class _FakeHUD:
    def __init__(self, font_small, font_big, assets):
        self.font_small = font_small
        self.font_big = font_big
        self.assets = assets


class _FakeAssets:
    """Minimal subset of Assets attributes used by Game._build_background/_build_ground."""
    def __init__(self, surface_factory):
        self.tree_sprites = [surface_factory((10, 10))]
        self.ground = type("GroundTiles", (), {})()
        self.ground.fill_mid = surface_factory((32, 32))


# ------------------------ fixtures ------------------------

@pytest.fixture
def game_for_tests(monkeypatch, headless_pygame, surface_factory):
    window = surface_factory((WIDTH, HEIGHT))

    screen_map = {
        GameState.START: _FakeScreen,
        GameState.PLAYING: _FakeScreen,
        GameState.GAME_OVER: _FakeScreen,
        GameState.SHOP: _FakeScreen,
    }

    def _fake_save_loader():
        return {
            "coins_bank": 123,
            "upgrades": {"shield_duration_level": 2, "x": 9},
            "high_score": 77,
        }

    fake_ground = _FakeGround()

    cfg = GameConfig(
        assets=_FakeAssets(surface_factory),
        save=SaveConfig(loader=_fake_save_loader, writer=lambda coins, upgrades, high: None),
        pygame=PygameConfig(window=window, clock=pg.time.Clock()),
        factories=FactoryConfig(
            background=lambda *a, **k: object(),
            player=lambda assets: object(),
            ground=lambda *a, **k: fake_ground,
            hud=_FakeHUD,
        ),
        screen_map=screen_map,
    )

    return Game(config=cfg, init_pygame=False)


# ------------------------ tests ------------------------

def test_init_loads_save_data_into_state(game_for_tests):
    g = game_for_tests
    assert g.ctx.progress.coins_bank == 123
    assert g.ctx.progress.upgrades["shield_duration_level"] == 2
    assert g.ctx.progress.high_score == 77


def test_set_screen_instantiates_screen(game_for_tests):
    g = game_for_tests
    assert isinstance(g.runtime.screen, _FakeScreen)

    g.set_screen(GameState.PLAYING)
    assert isinstance(g.runtime.screen, _FakeScreen)


def test_set_screen_resets_ground_only_on_start(game_for_tests):
    g = game_for_tests

    # __init__ calls set_screen(START) -> one reset
    assert g.ctx.ground.reset_calls == [float(BASE_SPEED)]

    g.set_screen(GameState.PLAYING)
    assert g.ctx.ground.reset_calls == [float(BASE_SPEED)]

    g.set_screen(GameState.START)
    assert g.ctx.ground.reset_calls == [float(BASE_SPEED), float(BASE_SPEED)]


def test_set_screen_temp_clears_except_game_over(game_for_tests):
    g = game_for_tests

    g.runtime.temp = {"some": "data"}

    # Going to PLAYING should clear temp
    g.set_screen(GameState.PLAYING)
    assert g.runtime.temp is None

    # Going to GAME_OVER keeps temp as-is
    g.runtime.temp = {"score": 123}
    g.set_screen(GameState.GAME_OVER)
    assert g.runtime.temp == {"score": 123}

    # Any other state clears again
    g.set_screen(GameState.SHOP)
    assert g.runtime.temp is None


def test_draw_calls_screen_draw_and_display_flip(monkeypatch, game_for_tests, capture):
    g = game_for_tests

    capture["n"] = 0
    monkeypatch.setattr(pg.display, "flip", lambda: capture.__setitem__("n", capture["n"] + 1))

    before = g.runtime.screen.draw_calls
    g.draw()

    assert g.runtime.screen.draw_calls == before + 1
    assert capture["n"] == 1


def test_run_exits_on_quit_event_and_saves(monkeypatch, game_for_tests, capture):
    g = game_for_tests

    class _Clock:
        def tick(self, fps):
            return 0

    g.runtime.clock = _Clock()

    capture["calls"] = 0

    def _fake_get():
        if capture["calls"] == 0:
            capture["calls"] += 1
            return [pg.event.Event(pg.QUIT)]
        return []

    monkeypatch.setattr(pg.event, "get", _fake_get)

    capture["saved_args"] = None
    g._save_writer = lambda coins, upgrades, high: capture.__setitem__("saved_args", (coins, upgrades, high))

    capture["quit_n"] = 0
    monkeypatch.setattr(pg, "quit", lambda: capture.__setitem__("quit_n", capture["quit_n"] + 1))

    g.run()

    assert capture["saved_args"] == (
        g.ctx.progress.coins_bank,
        g.ctx.progress.upgrades,
        g.ctx.progress.high_score,
    )
    assert capture["quit_n"] == 1
