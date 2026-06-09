#!/usr/bin/env bash
set -euo pipefail

echo "=== chaos-bot Dell/CachyOS setup (Arch Linux, NVIDIA CUDA) ==="

# 1. System packages (CachyOS/Arch — uses pacman)
echo "[1/7] Installing system packages..."
sudo pacman -Sy --noconfirm python python-pip python-venv v4l-utils || \
    echo "WARNING: pacman failed — ensure packages are installed manually"

# 2. Create venv
echo "[2/7] Setting up Python venv..."
if [[ ! -d "venv" ]]; then
    python -m venv venv
fi
source venv/bin/activate

# 3. Install CUDA PyTorch (must come before ultralytics)
echo "[3/7] Installing PyTorch with CUDA..."
pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124

# 4. Install remaining dependencies
echo "[4/7] Installing Python dependencies..."
pip install -r requirements-dell.txt

# 5. Download YOLOv11-nano weights
echo "[5/7] Downloading YOLOv11-nano weights..."
if [[ ! -f "models/yolo11n.pt" ]]; then
    python -c "
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

# 6. Export to TensorRT engine
echo "[6/7] Exporting YOLOv11-nano to TensorRT (this takes ~5 minutes)..."
if [[ ! -f "models/yolo11n.engine" ]]; then
    python scripts/export_yolo.py
else
    echo "  Already exists: models/yolo11n.engine"
fi

# 7. Verify V4L2 capture card
echo "[7/7] Checking for HDMI capture card..."
if [[ -e /dev/video0 ]]; then
    echo "  Found /dev/video0"
    v4l2-ctl --device=/dev/video0 --list-formats-ext 2>/dev/null | grep -A2 "MJPG" || \
        echo "  WARNING: MJPG not found — check capture card supports 120fps"
else
    echo "  /dev/video0 not found — plug in USB HDMI capture card and re-run"
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "Before running:"
echo "  1. Edit config.ini [kmbox] with IP/port/uid from KMBox Net screen"
echo "  2. Plug KMBox Net into gaming PC USB"
echo "  3. Test connectivity: source venv/bin/activate && python scripts/test_kmbox.py"
echo ""
echo "Run bot: source venv/bin/activate && python src/main.py"
