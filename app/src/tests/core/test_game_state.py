# @generated [all] ChatGPT : generate tests based on class implementation
from main.core.game_state import GameState


def test_game_state_has_expected_members():
    assert GameState.START.name == "START"
    assert GameState.PLAYING.name == "PLAYING"
    assert GameState.GAME_OVER.name == "GAME_OVER"
    assert GameState.SHOP.name == "SHOP"
    assert GameState.QUIT.name == "QUIT"


def test_game_state_contains_only_expected_members():
    expected = {"START", "PLAYING", "GAME_OVER", "SHOP", "QUIT"}
    actual = {state.name for state in GameState}
    assert actual == expected


def test_game_state_values_are_unique():
    values = [state.value for state in GameState]
    assert len(values) == len(set(values))
