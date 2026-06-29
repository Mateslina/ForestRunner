# @generated [all] ChatGPT : generate tests based on class implementation
import pytest

from main.core.assets.models import PowerupSprites
from tests.helpers.constants import POWERUP_KEYS


@pytest.fixture
def powerup_surfaces(surface_factory):
    sizes = {
        "shield": (1, 1),
        "double_coins": (2, 2),
        "double_score": (3, 3),
        "extra_life": (4, 4),
    }
    return {k: surface_factory(sizes[k]) for k in POWERUP_KEYS}


@pytest.mark.parametrize("key", POWERUP_KEYS)
def test_powerup_sprites_all_returns_expected_surface(powerup_surfaces, key):
    p = PowerupSprites(all=powerup_surfaces)
    assert p.all[key] is powerup_surfaces[key]


@pytest.mark.parametrize("missing_key", POWERUP_KEYS)
def test_powerup_sprites_all_raises_keyerror_for_missing_key(
    powerup_surfaces, missing_key
):
    data = dict(powerup_surfaces)
    data.pop(missing_key)
    p = PowerupSprites(all=data)

    with pytest.raises(KeyError):
        _ = p.all[missing_key]
