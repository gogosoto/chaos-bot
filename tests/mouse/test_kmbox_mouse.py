import sys
import os
import struct
import socket
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import pytest
from unittest.mock import MagicMock, patch


def make_config(ip="127.0.0.1", port=16234, uid="AABBCCDD"):
    cfg = MagicMock()
    cfg.kmbox_ip = ip
    cfg.kmbox_port = port
    cfg.kmbox_uid = uid
    cfg.target_cps = 10
    return cfg


def test_packet_is_28_bytes():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config())
    assert len(m._build_packet(cmd=0x0001, x=0, y=0)) == 28


def test_packet_uid_field():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config(uid="AABBCCDD"))
    pkt = m._build_packet(cmd=0x0001, x=0, y=0)
    assert struct.unpack_from("<I", pkt, 0)[0] == 0xAABBCCDD


def test_packet_cmd_field():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config())
    pkt = m._build_packet(cmd=0x0002, x=0, y=0)
    assert struct.unpack_from("<I", pkt, 8)[0] == 0x0002


def test_packet_xy_positive():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config())
    pkt = m._build_packet(cmd=0x0001, x=42, y=17)
    assert struct.unpack_from("<i", pkt, 12)[0] == 42
    assert struct.unpack_from("<i", pkt, 16)[0] == 17


def test_packet_xy_negative():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config())
    pkt = m._build_packet(cmd=0x0001, x=-10, y=-5)
    assert struct.unpack_from("<i", pkt, 12)[0] == -10
    assert struct.unpack_from("<i", pkt, 16)[0] == -5


def test_send_move_calls_sendto():
    from mouse.kmbox_mouse import KMBoxMouse
    mock_sock = MagicMock()
    with patch("socket.socket", return_value=mock_sock):
        m = KMBoxMouse(make_config(ip="10.0.0.5", port=6234))
        m.send_move(5, -3)
    assert mock_sock.sendto.called
    pkt, addr = mock_sock.sendto.call_args[0]
    assert len(pkt) == 28
    assert addr == ("10.0.0.5", 6234)


def test_send_move_xy_in_packet():
    from mouse.kmbox_mouse import KMBoxMouse
    mock_sock = MagicMock()
    with patch("socket.socket", return_value=mock_sock):
        m = KMBoxMouse(make_config())
        m.send_move(100, 50)
    pkt = mock_sock.sendto.call_args[0][0]
    assert struct.unpack_from("<i", pkt, 12)[0] == 100
    assert struct.unpack_from("<i", pkt, 16)[0] == 50


def test_send_click_sends_two_packets():
    from mouse.kmbox_mouse import KMBoxMouse
    mock_sock = MagicMock()
    with patch("socket.socket", return_value=mock_sock):
        m = KMBoxMouse(make_config())
        m.send_click(delay_before_click=0)
    assert mock_sock.sendto.call_count == 2


def test_udp_socket_created():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket") as mock_cls:
        KMBoxMouse(make_config())
    mock_cls.assert_called_with(socket.AF_INET, socket.SOCK_DGRAM)


def test_uid_parsed_correctly():
    from mouse.kmbox_mouse import KMBoxMouse
    with patch("socket.socket"):
        m = KMBoxMouse(make_config(uid="DEADBEEF"))
    assert m._uid == 0xDEADBEEF
