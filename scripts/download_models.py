#!/usr/bin/env python3
"""
Download ML models for Chaos Bot.
MediaPipe Pose + YOLOv8-Nano + quantized variants.
"""

import os
import sys
from pathlib import Path
import urllib.request
import urllib.error
import hashlib


# Model URLs and expected sizes
MODELS = {
    'mediapipe_pose': {
        'url': 'https://storage.googleapis.com/mediapipe/tasks/vision/pose_landmarker_lite.tflite',
        'path': 'models/pose_landmarker_lite.tflite',
        'size_mb': 6
    },
    'yolov8_nano': {
        'url': 'https://github.com/ultralytics/assets/releases/download/v8.1.0/yolov8n.pt',
        'path': 'models/yolov8n.pt',
        'size_mb': 7,
        'auto': True  # ultralytics will auto-download
    }
}


def create_dirs():
    """Create model directories."""
    Path('models').mkdir(exist_ok=True)
    Path('models/int8_quantized').mkdir(exist_ok=True)
    Path('models/tensorrt').mkdir(exist_ok=True)
    print("✓ Model directories created")


def download_file(url, dest, size_mb=None):
    """Download file with progress."""
    try:
        print(f"  Downloading {url}...")

        # Implement progress callback
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(100, int(100.0 * downloaded / total_size))
            bar = '█' * (percent // 5) + '░' * (20 - percent // 5)
            sys.stdout.write(f'\r  [{bar}] {percent}%')
            sys.stdout.flush()

        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest, progress)
        print()

        # Verify file size
        file_size_mb = Path(dest).stat().st_size / (1024 * 1024)
        if size_mb and abs(file_size_mb - size_mb) > 1:
            print(f"  ⚠ Warning: Expected {size_mb}MB, got {file_size_mb:.1f}MB")

        return True

    except urllib.error.URLError as e:
        print(f"\n  ✗ Download failed: {e}")
        return False
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def setup_yolo():
    """Setup YOLOv8 (auto-downloads on first use)."""
    try:
        print("Setting up YOLOv8-Nano...")
        from ultralytics import YOLO
        model = YOLO('yolov8n.pt')
        print("✓ YOLOv8-Nano ready (saved to ~/.cache/ultralytics/)")
        return True
    except Exception as e:
        print(f"⚠ YOLOv8 setup: {e}")
        print("  (Will be downloaded on first run)")
        return True


def download_models():
    """Download all required models."""
    create_dirs()

    print()
    print("Downloading models...")
    print()

    success_count = 0

    # MediaPipe Pose
    print("1. MediaPipe Pose Landmarker")
    if Path('models/pose_landmarker_lite.tflite').exists():
        print("  ✓ Already downloaded")
        success_count += 1
    else:
        if download_file(
            MODELS['mediapipe_pose']['url'],
            MODELS['mediapipe_pose']['path'],
            MODELS['mediapipe_pose']['size_mb']
        ):
            print("  ✓ Downloaded")
            success_count += 1

    # YOLOv8-Nano
    print()
    print("2. YOLOv8-Nano Object Detector")
    if setup_yolo():
        success_count += 1

    print()
    print("=" * 50)
    print(f"Downloaded {success_count}/2 models")
    print("=" * 50)

    if success_count == 2:
        print("✓ All models ready!")
        return 0
    else:
        print("⚠ Some models may need manual download")
        print("See HARDWARE_GUIDE.md for instructions")
        return 1


def convert_to_int8_quantized():
    """Convert models to INT8 for faster inference."""
    print()
    print("(Optional) Converting to INT8 quantized...")
    print("This step requires TensorFlow/ONNX tools")
    print("For now, FP32 models will be used")
    print()


def convert_to_tensorrt():
    """Convert YOLOv8 to TensorRT for Jetson optimization."""
    print()
    print("(Optional) Preparing for TensorRT conversion...")
    print("Run: python3 scripts/convert_to_tensorrt.py")
    print()


def main():
    print()
    print("=" * 50)
    print("Chaos Bot ML Model Downloader")
    print("=" * 50)
    print()

    result = download_models()
    convert_to_int8_quantized()
    convert_to_tensorrt()

    print("Next: Run 'python3 src/main.py' to start Chaos Bot")
    print()

    return result


if __name__ == '__main__':
    sys.exit(main())
