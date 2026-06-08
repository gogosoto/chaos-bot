#!/bin/bash

# Chaos Bot Jetson Setup Script
# Automates installation of all dependencies and ML models

set -e

echo "=========================================="
echo "Chaos Bot — Jetson Setup Script"
echo "=========================================="

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Jetson
if ! [ -f /etc/lsb-release-jetson ]; then
    echo -e "${YELLOW}Warning: This script is optimized for Jetson. Detected non-Jetson system.${NC}"
    echo "Continuing anyway (may have missing CUDA optimizations)..."
fi

# Step 1: System updates
echo -e "${GREEN}[1/6] Updating system packages...${NC}"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-dev

# Step 2: Install system dependencies
echo -e "${GREEN}[2/6] Installing system dependencies...${NC}"
sudo apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libjpeg-turbo8 \
    libv4l-0 \
    v4l-utils \
    ffmpeg \
    libatlas-base-dev \
    libjasper-dev \
    libtiff5-dev \
    libjasper-dev \
    libharfbuzz0b \
    libwebp6 \
    libtiff5 \
    libjasper-dev \
    libharfbuzz0b \
    libwebp6

# Step 3: Upgrade pip and install Python dependencies
echo -e "${GREEN}[3/6] Installing Python dependencies...${NC}"
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements-jetson.txt

# Step 4: Download ML models
echo -e "${GREEN}[4/6] Downloading ML models...${NC}"
mkdir -p models/int8_quantized

echo "  - MediaPipe Pose Landmarker..."
wget -q -O models/pose_landmarker_lite.tflite \
    https://storage.googleapis.com/mediapipe/tasks/vision/pose_landmarker_lite.tflite \
    2>/dev/null || echo "    Warning: Manual download required (see HARDWARE_GUIDE.md)"

echo "  - YOLOv8 Nano..."
python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" 2>/dev/null || echo "    (Model will be auto-downloaded on first run)"

# Step 5: Setup CircuitPython on Raspberry Pi Pico (if connected)
echo -e "${GREEN}[5/6] Checking Raspberry Pi Pico...${NC}"
if ls /dev/ttyACM* 2>/dev/null | grep -q .; then
    echo "  Found Pico at $(ls /dev/ttyACM*)"
    echo "  Run 'python3 scripts/flash_pico.py' to flash CircuitPython"
else
    echo "  No Pico detected (optional, can flash later)"
fi

# Step 6: Test setup
echo -e "${GREEN}[6/6] Testing hardware setup...${NC}"
echo "  Testing video capture..."
if v4l2-ctl --list-devices 2>/dev/null | grep -q video; then
    echo "    ✓ Video device found"
else
    echo "    ⚠ No video device detected (HDMI capture dongle not connected)"
fi

echo ""
echo -e "${GREEN}=========================================="
echo "Setup complete! Next steps:"
echo "=========================================${NC}"
echo ""
echo "1. Start Chaos Bot:"
echo "   python3 src/main.py"
echo ""
echo "2. Open web dashboard:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "3. Configure for your game in web UI"
echo "4. Launch CoD and start playing!"
echo ""
echo "For detailed setup, see HARDWARE_GUIDE.md"
echo ""
