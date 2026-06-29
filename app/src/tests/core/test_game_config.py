# @generated [all] ChatGPT : generate tests based on class implementation
from dataclasses import is_dataclass

from main.core.game_config import (
    GameConfig,
    SaveConfig,
    PygameConfig,
    FactoryConfig,
    FontConfig,
)


def test_game_config_is_dataclass():
    assert is_dataclass(GameConfig)


def test_game_config_defaults_are_independent_instances():
    a = GameConfig()
    b = GameConfig()

    # these must not be shared between instances (default_factory)
    assert a.save is not b.save
    assert a.pygame is not b.pygame
    assert a.factories is not b.factories
    assert a.fonts is not b.fonts


def test_game_config_default_fields_are_expected_types():
    cfg = GameConfig()

    assert cfg.assets is None
    assert cfg.screen_map is None

    assert isinstance(cfg.save, SaveConfig)
    assert isinstance(cfg.pygame, PygameConfig)
    assert isinstance(cfg.factories, FactoryConfig)
    assert isinstance(cfg.fonts, FontConfig)


def test_font_config_defaults():
    fonts = FontConfig()

    assert fonts.name == "arialunicode"
    assert fonts.small_size == 28
    assert fonts.big_size == 56


def test_pygame_config_defaults():
    pg_cfg = PygameConfig()
    assert pg_cfg.window is None
    assert pg_cfg.clock is None


def test_save_config_has_callable_loader_and_writer():
    save = SaveConfig()
    assert callable(save.loader)
    assert callable(save.writer)
