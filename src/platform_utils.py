import os
import platform


def is_mac_m1() -> bool:
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def is_jetson() -> bool:
    return (
        platform.machine() == "aarch64"
        and os.path.exists("/etc/nv_tegra_release")
    )


def is_cuda_linux() -> bool:
    """True when running on Linux with a CUDA-capable GPU (e.g. Dell RTX A2000)."""
    if platform.system() != "Linux":
        return False
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def device_label() -> str:
    """
    Returns a string identifying the inference backend to use:
      'jetson'     — Jetson Orin Nano (TensorRT)
      'mac-m1'     — Apple Silicon (MPS)
      'cuda-linux' — Linux with CUDA GPU, e.g. Dell RTX A2000
      'linux'      — Linux CPU fallback
    """
    if is_jetson():
        return "jetson"
    if is_mac_m1():
        return "mac-m1"
    if is_cuda_linux():
        return "cuda-linux"
    return "linux"
