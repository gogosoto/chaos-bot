import sys
import os
import importlib
import pytest
from unittest.mock import patch, MagicMock


def _get_module():
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    import platform_utils
    importlib.reload(platform_utils)
    return platform_utils


def test_is_mac_m1_true(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    importlib.reload(m)
    assert m.is_mac_m1() is True


def test_is_mac_m1_false_on_intel(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    importlib.reload(m)
    assert m.is_mac_m1() is False


def test_is_jetson_true(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.machine", lambda: "aarch64")
    monkeypatch.setattr("os.path.exists", lambda p: True if "nv_tegra" in p else False)
    importlib.reload(m)
    assert m.is_jetson() is True


def test_is_jetson_false_wrong_arch(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    monkeypatch.setattr("os.path.exists", lambda p: False)
    importlib.reload(m)
    assert m.is_jetson() is False


def test_is_cuda_linux_true(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    with patch.dict("sys.modules", {"torch": mock_torch}):
        importlib.reload(m)
        assert m.is_cuda_linux() is True


def test_is_cuda_linux_false_no_cuda(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Linux")
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    with patch.dict("sys.modules", {"torch": mock_torch}):
        importlib.reload(m)
        assert m.is_cuda_linux() is False


def test_is_cuda_linux_false_on_mac(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    with patch.dict("sys.modules", {"torch": mock_torch}):
        importlib.reload(m)
        assert m.is_cuda_linux() is False


def test_device_label_jetson(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "aarch64")
    monkeypatch.setattr("os.path.exists", lambda p: True if "nv_tegra" in p else False)
    with patch.dict("sys.modules", {"torch": MagicMock()}):
        importlib.reload(m)
        assert m.device_label() == "jetson"


def test_device_label_mac(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setattr("platform.machine", lambda: "arm64")
    monkeypatch.setattr("os.path.exists", lambda p: False)
    importlib.reload(m)
    assert m.device_label() == "mac-m1"


def test_device_label_cuda_linux(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    monkeypatch.setattr("os.path.exists", lambda p: False)
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = True
    with patch.dict("sys.modules", {"torch": mock_torch}):
        importlib.reload(m)
        assert m.device_label() == "cuda-linux"


def test_device_label_cpu_fallback(monkeypatch):
    m = _get_module()
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setattr("platform.machine", lambda: "x86_64")
    monkeypatch.setattr("os.path.exists", lambda p: False)
    mock_torch = MagicMock()
    mock_torch.cuda.is_available.return_value = False
    with patch.dict("sys.modules", {"torch": mock_torch}):
        importlib.reload(m)
        assert m.device_label() == "linux"
