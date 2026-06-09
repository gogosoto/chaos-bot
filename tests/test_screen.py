import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from unittest.mock import MagicMock, patch
import numpy as np


def make_config():
    cfg = MagicMock()
    cfg.capture_device = "/dev/video0"
    cfg.capture_width = 1920
    cfg.capture_height = 1080
    cfg.capture_fps = 120
    cfg.game_width = 2560
    cfg.game_height = 1440
    cfg.auto_detect_resolution = False
    cfg.resolution_x = 1920
    cfg.resolution_y = 1080
    cfg.screen_center_offset = 0
    cfg.capture_fov_x = 256
    cfg.capture_fov_y = 256
    cfg.aim_fov_x = 256
    cfg.aim_fov_y = 256
    cfg.group_close_target_blobs_threshold = (3, 3)
    cfg.upper_color = np.array([63, 255, 255])
    cfg.lower_color = np.array([58, 210, 80])
    cfg.aim_height = 0.5
    cfg.trigger_threshold = 8
    cfg.debug = False
    cfg.detection_mode = "color"
    return cfg


def test_screen_opens_v4l2_device():
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.side_effect = lambda prop: {2: 1920, 3: 1080}.get(prop, 120)
    with patch("cv2.VideoCapture", return_value=mock_cap) as mock_cv:
        import screen as screen_mod
        import importlib; importlib.reload(screen_mod)
        screen_mod.Screen(make_config())
    assert mock_cv.called


def test_scale_x_computed():
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.return_value = 1920
    with patch("cv2.VideoCapture", return_value=mock_cap):
        import screen as screen_mod
        import importlib; importlib.reload(screen_mod)
        s = screen_mod.Screen(make_config())
    assert abs(s.scale_x - (2560 / 1920)) < 0.001


def test_scale_y_computed():
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    mock_cap.get.return_value = 1080
    with patch("cv2.VideoCapture", return_value=mock_cap):
        import screen as screen_mod
        import importlib; importlib.reload(screen_mod)
        s = screen_mod.Screen(make_config())
    assert abs(s.scale_y - (1440 / 1080)) < 0.001


def test_screenshot_returns_crop():
    mock_cap = MagicMock()
    mock_cap.isOpened.return_value = True
    fake_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    fake_frame[412:668, 832:1088] = 42
    mock_cap.read.return_value = (True, fake_frame)
    mock_cap.get.return_value = 1920
    with patch("cv2.VideoCapture", return_value=mock_cap):
        import screen as screen_mod
        import importlib; importlib.reload(screen_mod)
        s = screen_mod.Screen(make_config())
        result = s.screenshot(region=(832, 412, 1088, 668))
    assert result.shape == (256, 256, 3)
    assert result[0, 0, 0] == 42
