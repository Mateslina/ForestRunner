# @generated [all] ChatGPT : generate tests based on class implementation
from main.ui.screens.base import BaseScreen
from tests.helpers.fakes import GameStub


def test_base_screen_stores_game_reference(surface_factory):
    g = GameStub(surface_factory)
    s = BaseScreen(g)
    assert s.game is g
