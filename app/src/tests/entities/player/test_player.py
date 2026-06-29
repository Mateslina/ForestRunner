# @generated [all] ChatGPT : generate tests based on class implementation
from types import SimpleNamespace

import pytest

from main.core.constants import GROUND_Y, JUMP_VELOCITY, PLAYER_X
from main.entities.player.player import Player
from tests.helpers.fakes import BlitSpy
from tests.helpers.fakes import GroundSolidSpy


@pytest.fixture
def player(player_frames_40x60_40x30):
    assets = SimpleNamespace(player=player_frames_40x60_40x30)
    return Player(assets)


def test_init_sets_rect_on_ground_and_sizes(player: Player):
    assert player.geom.stand_w == 40
    assert player.geom.stand_h == 60
    assert player.geom.crouch_w == 40
    assert player.geom.crouch_h == 30

    assert player.rect.x == PLAYER_X
    assert player.rect.bottom == GROUND_Y
    assert player.on_ground is True
    assert player.motion.crouching is False


def test_jump_only_when_on_ground(player: Player):
    assert player.on_ground is True

    player.jump()
    assert player.on_ground is False
    assert player.motion.velocity == JUMP_VELOCITY

    v = player.motion.velocity
    player.jump()
    assert player.motion.velocity == v


def test_set_crouch_blocked_in_air(player: Player):
    player.motion.on_ground = False
    player.set_crouch(True)
    assert player.motion.crouching is False


def test_set_crouch_on_ground_updates_rect_size_and_y(player: Player):
    player.motion.on_ground = True
    y0 = player.rect.y

    player.set_crouch(True)

    assert player.motion.crouching is True
    assert player.rect.size == (40, 30)
    assert player.rect.y == y0 + 30

    player.set_crouch(False)
    assert player.motion.crouching is False
    assert player.rect.size == (40, 60)


def test_give_and_consume_shield(player: Player):
    assert player.shield_active is False

    player.give_shield(1.5)
    assert player.shield_active is True
    assert player.buffs.shield_time == pytest.approx(1.5)

    player.consume_shield()
    assert player.shield_active is False
    assert player.buffs.shield_time == 0.0


def test_set_invulnerable_sets_timer_and_property(player: Player):
    assert player.invulnerable is False
    player.set_invulnerable(0.7)
    assert player.invulnerable is True
    assert player.buffs.invuln_time == pytest.approx(0.7)


def test_respawn_resets_motion_and_position(player: Player):
    player.motion.velocity = 123.0
    player.motion.crouching = True
    player.motion.on_ground = False
    player.geom.y = float(GROUND_Y - player.geom.stand_h - 100.0)
    player.sync_rect()

    player.respawn()

    assert player.motion.velocity == 0.0
    assert player.motion.crouching is False
    assert player.motion.on_ground is True
    assert player.geom.y == pytest.approx(float(GROUND_Y - player.geom.stand_h))
    assert player.rect.bottom == GROUND_Y
    assert player.rect.size == (player.geom.stand_w, player.geom.stand_h)


def test_current_sprite_branches(player: Player):
    player.motion.on_ground = False
    assert player._current_sprite() is player.sprites.run_frames[0]

    player.motion.on_ground = True
    player.motion.crouching = True
    player.anim.crouch_i = 1
    assert player._current_sprite() is player.sprites.crouch_frames[1]

    player.motion.crouching = False
    player.anim.run_i = 1
    assert player._current_sprite() is player.sprites.run_frames[1]


def test_update_delegates_to_controller(player: Player):
    calls = {"p": None, "dt": None, "ground": None, "speed": None}

    class _CtrlSpy:
        def update(self, p, dt, ground, speed):
            calls["p"] = p
            calls["dt"] = float(dt)
            calls["ground"] = ground
            calls["speed"] = float(speed)

    player.controller = _CtrlSpy()

    g = GroundSolidSpy(solid=True)
    player.update(0.25, g, 321.0)

    assert calls["p"] is player
    assert calls["dt"] == pytest.approx(0.25)
    assert calls["ground"] is g
    assert calls["speed"] == pytest.approx(321.0)


def test_draw_calls_shield_glow_when_active(monkeypatch, player: Player):
    screen = BlitSpy(size=(300, 200))

    glow_calls = {"n": 0}

    def _fake_glow(*a, **k):
        glow_calls["n"] += 1

    monkeypatch.setattr("main.entities.player.player.draw_shield_glow", _fake_glow)

    monkeypatch.setattr(
        "main.entities.player.player.sprite_visible_during_invuln",
        lambda invulnerable, blink_ms=100: True,
    )

    player.give_shield(1.0)
    player.draw(screen)

    assert glow_calls["n"] == 1
    assert len(screen.calls) == 1


def test_draw_skips_blit_when_invuln_invisible(monkeypatch, player: Player):
    screen = BlitSpy(size=(300, 200))

    monkeypatch.setattr(
        "main.entities.player.player.sprite_visible_during_invuln",
        lambda invulnerable, blink_ms=100: False,
    )

    player.set_invulnerable(1.0)
    player.draw(screen)

    assert not screen.calls


def test_draw_blits_with_correct_offset_stand_vs_crouch(monkeypatch, player: Player):
    screen = BlitSpy(size=(300, 200))

    monkeypatch.setattr(
        "main.entities.player.player.sprite_visible_during_invuln",
        lambda invulnerable, blink_ms=100: True,
    )

    player.motion.crouching = False
    player.sync_rect()
    player.draw(screen)

    assert len(screen.calls) == 1
    _, (x0, y0) = screen.calls[-1]
    assert x0 == player.rect.x
    assert y0 == player.rect.y + 15

    player.set_crouch(True)
    player.draw(screen)

    assert len(screen.calls) == 2
    _, (x1, y1) = screen.calls[-1]
    assert x1 == player.rect.x
    assert y1 == player.rect.y + 4
