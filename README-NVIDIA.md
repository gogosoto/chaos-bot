# Chaos Bot — Nvidia Jetson Optimized

Chaos Bot is an **Nvidia Jetson-specific** fork of Unibot optimized for **Call of Duty** with GPU-accelerated ML inference.

## Hardware Target

- **Nvidia Jetson Orin Nano** (primary)
- **Jetson AGX Orin** (enterprise)
- **Jetson Xavier NX** (budget alternative)

## Key Differences from Unibot

### ML-Powered Detection

1. **MediaPipe Pose** — Real-time body keypoint detection
   - Detects standing/crouching/prone at 50-60 FPS
   - Works with partial visibility (smoke, distance)
   - Adapts to different lighting conditions

2. **YOLOv8-Nano Object Detection** — Head/body detection
   - Identifies enemy heads specifically
   - Distinguishes friendlies (blue) vs enemies (red)
   - Reduces false positives on environment

3. **Adaptive Color Learning** — Auto HSV calibration
   - Game intro: learns enemy outline color
   - Per-map color adjustment
   - No manual tuning needed

### GPU Acceleration

- TensorRT optimized inference (~10x faster than CPU)
- CUDA support for parallel processing
- Real-time performance at 60 FPS with ML

## Installation

### Prerequisites

```bash
# Jetson OS (JetPack 5.1+)
sudo apt update && sudo apt upgrade
sudo apt install python3-pip python3-dev

# CUDA/cuDNN (pre-installed on JetPack)
nvcc --version
```

### Setup

```bash
# Clone repo
git clone https://github.com/gogosoto/chaos-bot.git
cd chaos-bot

# Install dependencies
pip install -r requirements-jetson.txt

# Download ML models
python3 scripts/download_models.py
```

## Configuration

### config.ini (CoD-optimized)

```ini
[ml_detection]
enabled = true
pose_model = mediapipe
object_detection = yolov8-nano
adaptive_color_learning = true

[aim]
bot_input_type = microcontroller_serial
speed = 1.2
aim_smoothing_factor = 0.3

[shape_validation]
enabled = true
check_convexity = true
min_convexity_score = 0.4
```

## Running Chaos Bot

### Local Mode

```bash
python3 src/main.py
```

Web dashboard: `http://localhost:5000`

### Headless Mode (Jetson only)

```bash
python3 src/main.py --headless
```

### With HDMI Capture

```bash
# Connect HDMI capture dongle via USB
python3 src/main.py --capture-device /dev/video0
```

## Performance

| Task | FPS | Latency |
|------|-----|---------|
| Screen capture | 60 | ~16ms |
| MediaPipe Pose | 50-60 | ~15ms |
| YOLOv8-Nano | 40-50 | ~20ms |
| Mouse control | 60 | <10ms |
| **Total pipeline** | **40-50** | **~50-70ms** |

## Architecture

```
HDMI Capture → Frame Buffer
                     ↓
            MediaPipe Pose (GPU)
                     ↓
            YOLOv8-Nano (GPU)
                     ↓
            Adaptive Color Bounds
                     ↓
            Aim + Trigger Logic
                     ↓
            Raspberry Pi Pico (Serial)
                     ↓
            PC USB Mouse
```

## Model Files

Models are downloaded on first run and cached locally:

- `models/mediapipe_pose.tflite` (~6 MB)
- `models/yolov8n.pt` (~7 MB)
- `models/int8_quantized/` (optimized for Jetson)

## Jetson-Specific Optimizations

### TensorRT Conversion

```bash
# Convert PyTorch models to TensorRT for 5-10x speedup
python3 scripts/convert_to_tensorrt.py --model yolov8n
```

### Power Management

```bash
# Jetson Orin Nano runs hot — set aggressive cooling
sudo jetson_clocks  # Max performance mode
sudo nvpmodel -m 0  # Max N-Core mode (default)
```

### Memory Usage

- Jetson Orin Nano: 8GB LPDDR5 (shared GPU/CPU)
- MediaPipe: ~200 MB
- YOLOv8: ~150 MB
- Unibot: ~100 MB
- **Headroom: ~7.5 GB available**

## Tuning for Call of Duty

### Per-Map Calibration

1. Launch CoD, enter map
2. Open Chaos Bot web UI: `http://localhost:5000`
3. Wait 30 seconds for adaptive learning
4. HSV bounds auto-adjust
5. Play

### Manual Override

```ini
[screen]
lower_color = 0, 100, 100      # Red lower bound
upper_color = 30, 255, 255     # Red upper bound
adaptive_learning_speed = 0.1   # 0.0 = off, 1.0 = aggressive
```

## Troubleshooting

### Models not downloading

```bash
python3 scripts/download_models.py --verbose
```

### TensorRT conversion fails

```bash
# Fall back to ONNX runtime (slower but always works)
export USE_ONNX=1
python3 src/main.py
```

### Jetson thermal throttling

```bash
# Check temperature
tegrastats
# Reduce inference fps if > 80°C
```

## Building Hardware

See [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) for complete Bill of Materials and assembly.

## Contributing

Chaos Bot is optimized for Jetson hardware. For CPU-only, use [Unibot](https://github.com/gogosoto/Unibot).

## License

GNU General Public License v3.0 — See LICENSE.txt
