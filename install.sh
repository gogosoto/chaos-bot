#!/usr/bin/env bash
set -euo pipefail

echo "=== chaos-bot Jetson Orin Nano Super setup ==="
echo "Requires: JetPack 6.1, NVMe SSD mounted at /"

# 1. System packages (Ubuntu/apt — JetPack base OS)
echo "[1/7] Installing system packages..."
sudo apt update -q
sudo apt install -y python3-pip python3-venv v4l-utils libopencv-dev

# 2. Create venv
echo "[2/7] Setting up Python venv..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv --system-site-packages
fi
source venv/bin/activate

# 3. Install JetPack PyTorch wheel
echo "[3/7] Installing JetPack-optimized PyTorch..."
TORCH_WHL="https://developer.download.nvidia.com/compute/redist/jp/v61/pytorch/torch-2.3.0a0+ebedce2.nv24.1-cp310-cp310-linux_aarch64.whl"
pip install --upgrade pip
pip install "${TORCH_WHL}" || echo "WARNING: JetPack torch wheel failed — check JetPack version at developer.nvidia.com/embedded/jetpack"

# 4. Install Python dependencies
echo "[4/7] Installing Python dependencies..."
pip install -r requirements-jetson.txt

# 5. Download weights
echo "[5/7] Downloading YOLOv11-nano weights..."
if [[ ! -f "models/yolo11n.pt" ]]; then
    python3 -c "
from ultralytics import YOLO
import shutil, os
model = YOLO('yolo11n.pt')
os.makedirs('models', exist_ok=True)
if os.path.exists('yolo11n.pt'):
    shutil.move('yolo11n.pt', 'models/yolo11n.pt')
print('Weights saved to models/yolo11n.pt')
"
else
    echo "  Already exists: models/yolo11n.pt"
fi

# 6. Export to TensorRT
echo "[6/7] Exporting to TensorRT INT8 engine (~5 minutes)..."
if [[ ! -f "models/yolo11n.engine" ]]; then
    python3 scripts/export_yolo.py
else
    echo "  Already exists: models/yolo11n.engine"
fi

# 7. Verify V4L2 capture card
echo "[7/7] Checking for HDMI capture card..."
if [[ -e /dev/video0 ]]; then
    echo "  Found /dev/video0"
    v4l2-ctl --device=/dev/video0 --list-formats-ext 2>/dev/null | grep -A2 "MJPG" || \
        echo "  WARNING: MJPG not listed — confirm card supports 1080p120"
else
    echo "  /dev/video0 not found — plug in USB HDMI capture card"
fi

# Optional: systemd service
SERVICE_SRC="scripts/chaos-bot.service"
if [[ -f "${SERVICE_SRC}" ]]; then
    read -rp "Install systemd autostart service? (y/N): " ans
    if [[ "${ans:-N}" =~ ^[Yy]$ ]]; then
        sudo cp "${SERVICE_SRC}" /etc/systemd/system/
        sudo systemctl enable chaos-bot
        echo "Service installed. Start: sudo systemctl start chaos-bot"
    fi
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Before running:"
echo "  1. Edit config.ini [kmbox] with IP/port/uid from KMBox Net screen"
echo "  2. Test KMBox: source venv/bin/activate && python scripts/test_kmbox.py"
echo ""
echo "Run bot: source venv/bin/activate && python3 src/main.py"
