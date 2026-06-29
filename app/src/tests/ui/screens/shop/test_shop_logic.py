# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace

import pytest

from main.ui.screens.shop.shop_logic import ShopLogic, DEFAULT_SHOP_ITEMS


@pytest.fixture
def progress():
    return SimpleNamespace(coins_bank=0, upgrades={})


@pytest.fixture
def shop_items():
    return list(DEFAULT_SHOP_ITEMS[:2])


@pytest.fixture
def logic(progress, shop_items):
    return ShopLogic(progress, shop_items)


def test_level_defaults_to_zero(logic):
    assert logic.level("missing_key") == 0


def test_cost_increases_with_level(progress, shop_items):
    logic = ShopLogic(progress, shop_items)
    item = shop_items[0]

    assert logic.cost(item) == item.base_cost

    progress.upgrades[item.key] = 2
    assert logic.cost(item) == item.base_cost + item.cost_step * 2


def test_can_buy_requires_enough_coins_and_not_maxed(progress, shop_items):
    logic = ShopLogic(progress, shop_items)
    item = shop_items[0]

    progress.coins_bank = logic.cost(item)
    assert logic.can_buy(item) is True

    progress.coins_bank = logic.cost(item) - 1
    assert logic.can_buy(item) is False

    progress.coins_bank = 10**9
    progress.upgrades[item.key] = item.max_level
    assert logic.can_buy(item) is False


def test_buy_updates_coins_and_level_when_allowed(progress, shop_items):
    logic = ShopLogic(progress, shop_items)
    item = shop_items[0]

    progress.coins_bank = 999
    before_lvl = logic.level(item.key)
    cost = logic.cost(item)
    before_coins = progress.coins_bank

    ok = logic.buy(item)
    assert ok is True
    assert logic.level(item.key) == before_lvl + 1
    assert progress.coins_bank == before_coins - cost


def test_buy_returns_false_and_changes_nothing_when_not_allowed(progress, shop_items):
    logic = ShopLogic(progress, shop_items)
    item = shop_items[0]

    progress.coins_bank = 0
    before_lvl = logic.level(item.key)
    before_coins = progress.coins_bank
    ok = logic.buy(item)

    assert ok is False
    assert logic.level(item.key) == before_lvl
    assert progress.coins_bank == before_coins

    progress.coins_bank = 999
    progress.upgrades[item.key] = item.max_level
    before_lvl = logic.level(item.key)
    before_coins = progress.coins_bank
    ok = logic.buy(item)

    assert ok is False
    assert logic.level(item.key) == before_lvl
    assert progress.coins_bank == before_coins
