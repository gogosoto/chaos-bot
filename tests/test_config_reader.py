import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest


MINIMAL_INI = """
[aim]
bot_input_type = kmbox
screen_center_offset = 0
aim_smoothing_factor = 0.0
speed = 1.0
y_speed_multiplier = 1.0
aim_height = 0.5

[communication]
microcontroller_ip = 0.0.0.0
microcontroller_port = 50256
com_port = 1

[kmbox]
kmbox_ip = 192.168.1.100
kmbox_port = 6234
kmbox_uid = AABBCCDD

[capture]
device = /dev/video0
capture_width = 1920
capture_height = 1080
capture_fps = 120
game_width = 2560
game_height = 1440

[detection]
mode = hybrid
yolo_model = models/yolo11n.pt
yolo_confidence = 0.5

[screen]
group_close_target_blobs_threshold = 3, 3
upper_color = 63, 255, 255
lower_color = 58, 210, 80
capture_fov_x = 256
capture_fov_y = 256
aim_fov_x = 256
aim_fov_y = 256
max_loops_per_sec = 60
auto_detect_resolution = false
resolution_x = 1920
resolution_y = 1080

[recoil]
mode = move
recoil_x = 0.0
recoil_y = 0.0
max_offset = 100
recover = 0.0

[trigger]
trigger_delay = 0
trigger_randomization = 30
trigger_threshold = 8

[rapid_fire]
target_cps = 10

[key_binds]
key_reload_config = 0x70
key_toggle_aim = 0x71
key_toggle_recoil = 0x72
key_exit = 0x73
key_trigger = 0x06
key_rapid_fire = 0x05
aim_keys = 0x01, 0x02

[debug]
enabled = false
always_on = false
display_mode = mask

[shape_validation]
enabled = false
check_aspect_ratio = false
aspect_ratio_min = 0.2
aspect_ratio_max = 0.8
check_area_threshold = false
min_blob_area = 10
max_blob_area = 10000
check_convexity = false
min_convexity_score = 0.7
check_solidity = false
min_solidity_score = 0.7
check_vertical_bias = false
vertical_bias_threshold = 0.6

[pose_detection]
pose_standing_threshold = 0.6
pose_crouching_threshold = 0.4
pose_prone_threshold = 0.2
pose_lead_standing = 0.3
pose_lead_crouching = 0.2
pose_lead_prone = 0.1
"""


@pytest.fixture
def cfg_path(tmp_path):
    p = tmp_path / "config.ini"
    p.write_text(MINIMAL_INI)
    return str(p)


def make_reader(cfg_path):
    from configReader import ConfigReader
    r = ConfigReader(path=cfg_path)
    r.read_config()
    return r


def test_bot_input_type_kmbox(cfg_path):
    assert make_reader(cfg_path).bot_input_type == "kmbox"

def test_kmbox_ip(cfg_path):
    assert make_reader(cfg_path).kmbox_ip == "192.168.1.100"

def test_kmbox_port(cfg_path):
    assert make_reader(cfg_path).kmbox_port == 6234

def test_kmbox_uid(cfg_path):
    assert make_reader(cfg_path).kmbox_uid == "AABBCCDD"

def test_capture_device(cfg_path):
    assert make_reader(cfg_path).capture_device == "/dev/video0"

def test_capture_width(cfg_path):
    assert make_reader(cfg_path).capture_width == 1920

def test_capture_height(cfg_path):
    assert make_reader(cfg_path).capture_height == 1080

def test_capture_fps(cfg_path):
    assert make_reader(cfg_path).capture_fps == 120

def test_game_width(cfg_path):
    assert make_reader(cfg_path).game_width == 2560

def test_game_height(cfg_path):
    assert make_reader(cfg_path).game_height == 1440

def test_detection_mode_hybrid(cfg_path):
    assert make_reader(cfg_path).detection_mode == "hybrid"

def test_yolo_model(cfg_path):
    assert make_reader(cfg_path).yolo_model == "models/yolo11n.pt"

def test_yolo_confidence(cfg_path):
    assert make_reader(cfg_path).yolo_confidence == 0.5
