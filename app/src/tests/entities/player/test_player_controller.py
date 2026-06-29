# @generated [all] ChatGPT : generate tests based on class implementation
from dataclasses import dataclass

import pytest

from main.core.constants import BASE_SPEED, GROUND_Y, GRAVITY, PLAYER_X
from main.entities.player.player_controller import PlayerController
from tests.helpers.fakes import GroundSolidSpy


@dataclass
class _Geom:
    y: float
    stand_w: float
    stand_h: float


@dataclass
class _Motion:
    velocity: float
    on_ground: bool
    crouching: bool


@dataclass
class _Buffs:
    shield_active: bool
    shield_time: float
    invuln_time: float


@dataclass
class _Anim:
    t: float
    run_i: int
    crouch_i: int


class _FakePlayer:
    def __init__(
        self,
        *,
        y: float,
        stand_w: float = 40.0,
        stand_h: float = 60.0,
        velocity: float = 0.0,
        on_ground: bool = False,
        crouching: bool = False,
        shield_active: bool = False,
        shield_time: float = 0.0,
        invuln_time: float = 0.0,
        t: float = 0.0,
        run_i: int = 0,
        crouch_i: int = 0,
    ):
        self.geom = _Geom(y=float(y), stand_w=float(stand_w), stand_h=float(stand_h))
        self.motion = _Motion(
            velocity=float(velocity),
            on_ground=bool(on_ground),
            crouching=bool(crouching),
        )
        self.buffs = _Buffs(
            shield_active=bool(shield_active),
            shield_time=float(shield_time),
            invuln_time=float(invuln_time),
        )
        self.anim = _Anim(t=float(t), run_i=int(run_i), crouch_i=int(crouch_i))
        self.sync_calls = 0

    def sync_rect(self):
        self.sync_calls += 1


def test_update_calls_sync_rect():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.0, ground=g, speed=BASE_SPEED)

    assert p.sync_calls == 1


def test_apply_gravity_increases_velocity_and_y():
    ctrl = PlayerController()
    p = _FakePlayer(y=10.0, velocity=0.0)
    g = GroundSolidSpy(solid=False)

    dt = 0.5
    ctrl.update(p, dt=dt, ground=g, speed=BASE_SPEED)

    assert p.motion.velocity == pytest.approx(GRAVITY * dt)
    assert p.geom.y == pytest.approx(10.0 + (GRAVITY * dt) * dt)


def test_resolve_ground_collision_snaps_to_ground_and_zeros_velocity_when_below_ground():
    ctrl = PlayerController()
    stand_h = 60.0
    ground_y = float(GROUND_Y - stand_h)

    p = _FakePlayer(y=ground_y + 5.0, stand_h=stand_h, velocity=123.0, on_ground=False)
    g = GroundSolidSpy(solid=True)

    ctrl.update(p, dt=0.0, ground=g, speed=BASE_SPEED)

    assert p.geom.y == pytest.approx(ground_y)
    assert p.motion.velocity == 0.0
    assert p.motion.on_ground is True

    assert len(g.calls) == 1
    x1, x2, min_ov = g.calls[0]
    assert x2 > x1
    assert x1 >= float(PLAYER_X)
    assert min_ov >= 1.0


def test_resolve_ground_collision_sets_on_ground_false_when_in_air_above_solid_ground():
    ctrl = PlayerController()
    stand_h = 60.0
    ground_y = float(GROUND_Y - stand_h)

    p = _FakePlayer(y=ground_y - 10.0, stand_h=stand_h, velocity=0.0, on_ground=True)
    g = GroundSolidSpy(solid=True)

    ctrl.update(p, dt=0.0, ground=g, speed=BASE_SPEED)

    assert p.geom.y == pytest.approx(ground_y - 10.0)
    assert p.motion.on_ground is False


def test_resolve_ground_collision_sets_on_ground_false_when_no_solid_ground():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0, on_ground=True)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.0, ground=g, speed=BASE_SPEED)

    assert p.motion.on_ground is False


def test_update_shield_decrements_and_expires():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0, shield_active=True, shield_time=0.2)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.3, ground=g, speed=BASE_SPEED)

    assert p.buffs.shield_time == 0.0
    assert p.buffs.shield_active is False


def test_update_shield_decrements_but_stays_active_when_time_left():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0, shield_active=True, shield_time=1.0)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.25, ground=g, speed=BASE_SPEED)

    assert p.buffs.shield_time == pytest.approx(0.75)
    assert p.buffs.shield_active is True


def test_update_invuln_decrements_to_zero():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0, invuln_time=0.2)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.25, ground=g, speed=BASE_SPEED)

    assert p.buffs.invuln_time == 0.0


def test_update_animation_resets_timer_when_airborne():
    ctrl = PlayerController()
    p = _FakePlayer(y=0.0, t=0.123, on_ground=False)
    g = GroundSolidSpy(solid=False)

    ctrl.update(p, dt=0.5, ground=g, speed=BASE_SPEED)

    assert p.anim.t == 0.0


def test_update_animation_toggles_run_frame_when_on_ground_and_not_crouching():
    ctrl = PlayerController()
    stand_h = 60.0
    ground_y = float(GROUND_Y - stand_h)

    p = _FakePlayer(
        y=ground_y,
        stand_h=stand_h,
        on_ground=True,
        crouching=False,
        run_i=0,
        t=0.0,
    )
    g = GroundSolidSpy(solid=True)

    ctrl.update(p, dt=0.15, ground=g, speed=BASE_SPEED)

    assert p.anim.run_i == 1
    assert p.anim.t == 0.0


def test_update_animation_toggles_crouch_frame_when_crouching():
    ctrl = PlayerController()
    stand_h = 60.0
    ground_y = float(GROUND_Y - stand_h)

    p = _FakePlayer(
        y=ground_y,
        stand_h=stand_h,
        on_ground=True,
        crouching=True,
        crouch_i=0,
        t=0.0,
    )
    g = GroundSolidSpy(solid=True)

    ctrl.update(p, dt=0.15, ground=g, speed=BASE_SPEED)

    assert p.anim.crouch_i == 1
    assert p.anim.t == 0.0


def test_update_animation_uses_speed_factor_faster_speed_faster_anim():
    ctrl = PlayerController()
    stand_h = 60.0
    ground_y = float(GROUND_Y - stand_h)
    g = GroundSolidSpy(solid=True)

    p_slow = _FakePlayer(y=ground_y, stand_h=stand_h, on_ground=True, run_i=0, t=0.0)
    p_fast = _FakePlayer(y=ground_y, stand_h=stand_h, on_ground=True, run_i=0, t=0.0)

    ctrl.update(p_slow, dt=0.06, ground=g, speed=BASE_SPEED)
    ctrl.update(p_fast, dt=0.06, ground=g, speed=BASE_SPEED * 3.0)

    assert p_slow.anim.run_i == 0
    assert p_fast.anim.run_i == 1
