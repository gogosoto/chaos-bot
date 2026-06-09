import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from unittest.mock import MagicMock


def make_cfg(speed=1.0, smoothing=1.0, y_mult=1.0, scale_x=1.0, scale_y=1.0,
             recoil_mode='move', recoil_x=0.0, recoil_y=0.0, max_offset=100, recover=0.0):
    cfg = MagicMock()
    cfg.speed = speed
    cfg.aim_smoothing_factor = smoothing
    cfg.y_speed_multiplier = y_mult
    cfg.aim_height = 0.5
    cfg.scale_x = scale_x
    cfg.scale_y = scale_y
    cfg.recoil_mode = recoil_mode
    cfg.recoil_x = recoil_x
    cfg.recoil_y = recoil_y
    cfg.max_offset = max_offset
    cfg.recoil_recover = recover
    return cfg


def test_scale_x_applied():
    from cheats import Cheats
    c = Cheats(make_cfg(scale_x=2.0, scale_y=1.0))
    c.calculate_aim(True, (10, 0))
    assert abs(c.move_x - 20.0) < 0.01

def test_scale_y_applied():
    from cheats import Cheats
    c = Cheats(make_cfg(scale_x=1.0, scale_y=3.0))
    c.calculate_aim(True, (0, 5))
    assert abs(c.move_y - 15.0) < 0.01

def test_scale_1_is_identity():
    from cheats import Cheats
    c = Cheats(make_cfg(scale_x=1.0, scale_y=1.0))
    c.calculate_aim(True, (8, 4))
    assert abs(c.move_x - 8.0) < 0.01
    assert abs(c.move_y - 4.0) < 0.01

def test_1440p_scale():
    from cheats import Cheats
    c = Cheats(make_cfg(scale_x=2560/1920, scale_y=1440/1080))
    c.calculate_aim(True, (30, 30))
    assert abs(c.move_x - 30 * (2560/1920)) < 0.01
    assert abs(c.move_y - 30 * (1440/1080)) < 0.01

def test_no_move_when_aim_off():
    from cheats import Cheats
    c = Cheats(make_cfg())
    c.calculate_aim(False, (10, 10))
    assert c.move_x == 0
    assert c.move_y == 0

def test_apply_recoil_no_crash_without_input_state():
    from cheats import Cheats
    c = Cheats(make_cfg(recoil_mode='move', recoil_x=1.0, recoil_y=1.0))
    c.apply_recoil(True, 0.016, input_state=None)
