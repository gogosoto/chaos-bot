# Chaos Bot — Quick Start

Fast-track to building a Call of Duty aim bot on Nvidia Jetson hardware.

## 1. Hardware (30 min)

Order parts from [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) (~$341):
- Jetson Orin Nano ($200)
- HDMI capture dongle ($30)
- Raspberry Pi Pico ($8)
- Power supply, microSD, Ethernet, enclosure

**Total lead time: 3-5 days**

## 2. Initial Setup (45 min)

On Jetson:
```bash
# Clone repo
git clone https://github.com/gogosoto/chaos-bot.git
cd chaos-bot

# Run setup script (automates everything)
chmod +x scripts/setup_jetson.sh
./scripts/setup_jetson.sh

# This will:
# - Update system packages
# - Install ML dependencies (MediaPipe, YOLOv8)
# - Download models (~15 MB)
# - Check Pico connection
```

## 3. Flash Pico (10 min)

If Pico is plugged in:
```bash
python3 scripts/flash_pico.py
```

This installs CircuitPython for USB mouse emulation.

## 4. Start Chaos Bot (2 min)

```bash
python3 src/main.py
```

Open web dashboard:
```
http://<jetson-ip>:5000
```

## 5. Configure for Your Game (5 min)

1. Launch Call of Duty
2. Go to Chaos Bot web UI
3. Wait ~30 seconds for adaptive color learning
4. Tune HSV bounds if needed (see "Color Tuning" below)
5. Press spacebar (default) to enable aim assist

## Color Tuning

### Fast Method (Recommended)

Use game presets:
- Click "Presets" in web UI
- Select "Call of Duty Red" (default for enemies)
- Play

### Manual Method

1. In web UI, go to "Color" tab
2. Adjust HSV sliders:
   - **H** (Hue): 0-30 for red outlines
   - **S** (Saturation): 150-255 for solid colors
   - **V** (Value): 100-200 for brightness
3. Watch preview box update on canvas
4. Test in-game

### Per-Map Learning

Each map has different lighting:
1. Start new game
2. Wait 30 seconds (auto-learning)
3. Boundaries auto-adjust

## Configuration

Edit `config.ini` for advanced tuning:

```ini
[aim]
speed = 1.2              # How fast to aim (0.5-2.0)
aim_smoothing_factor = 0.3

[ml_detection]
enabled = true           # Use ML pose detection
pose_model = mediapipe
object_detection = yolov8-nano

[pose_detection]
standing_threshold = 1.2
crouching_threshold = 0.7
prone_threshold = 0.4
```

## Performance Targets

| Metric | Target | What It Means |
|--------|--------|---------------|
| Latency | < 70ms | Time from enemy on screen → aim fired |
| FPS | 40-50 | ML inference speed |
| CPU Usage | < 60% | Keep Jetson cool |
| GPU Memory | < 2GB | Leave room for system |

Check current performance:
```bash
# Monitor in real-time
watch -n 1 'tegrastats'
```

## Troubleshooting

### No video capture
```bash
# Check USB device
lsusb | grep -i video

# Debug video
v4l2-ctl --list-devices
```

### Pico not detected
```bash
# Check serial
ls -la /dev/ttyACM*

# Reflash
python3 scripts/flash_pico.py --force
```

### ML models too slow
- Reduce input resolution in `config.ini`
- Disable YOLOv8 if pose alone is sufficient
- Use TensorRT: `python3 scripts/convert_to_tensorrt.py`

### Jetson thermal throttling
```bash
# Check temp
tegrastats | grep temp

# If > 80°C:
# - Add ventilation holes to enclosure
# - Reduce inference FPS
# - Add active cooling
```

## Next Steps

- [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md) — Full assembly & troubleshooting
- [README-NVIDIA.md](README-NVIDIA.md) — Detailed Jetson optimizations
- `config.ini` — Advanced tuning parameters

## Support

Issues? Check:
1. HARDWARE_GUIDE.md troubleshooting section
2. GitHub issues at https://github.com/gogosoto/chaos-bot/issues
3. Jetson docs: https://docs.nvidia.com/jetson/

---

**Ready to build?** Start with [HARDWARE_GUIDE.md](HARDWARE_GUIDE.md).
