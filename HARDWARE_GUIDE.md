# Chaos Bot Hardware Build Guide

Complete Bill of Materials and assembly instructions for a CoD-optimized Chaos Bot appliance.

## Bill of Materials

### Core Hardware

| Component | Model | Cost | Notes |
|-----------|-------|------|-------|
| **Main Processor** | Nvidia Jetson Orin Nano | $200 | GPU accelerated ML |
| **Video Capture** | HDMI to USB-C dongle | $30 | Elgato alternative, 4K capable |
| **HID Controller** | Raspberry Pi Pico | $8 | USB mouse emulation |
| **Power Supply** | 5V/5A USB-C | $20 | Jetson needs higher current |
| **Storage** | 256GB microSD (A2, V30) | $25 | Fast I/O for model caching |
| **Networking** | Gigabit Ethernet cable | $8 | Minimal latency (5ms vs 50ms WiFi) |
| **Enclosure** | 3D printed or aluminum | $35 | Passive cooling, compact |
| **Cooling** | 40mm USB fan (optional) | $15 | If ambient > 25°C |

**Total: ~$341**

### Optional Upgrades

- Jetson Orin NX ($250) — if Nano is unavailable
- Jetson AGX Orin ($599) — for multiple simultaneous instances
- 1TB SSD ($80) — if running large model library
- Active cooler block ($40) — for sustained gaming sessions

## Assembly

### Step 1: Prepare Jetson

1. Flash JetPack 5.1+ to microSD
   ```bash
   # On PC
   wget https://developer.nvidia.com/embedded/jetpack-sdks-archive
   # Follow flashing guide at https://docs.nvidia.com/jetson/jetpack/
   ```

2. Insert microSD and power on
3. Complete NVIDIA setup wizard

### Step 2: Connect Capture Card

```
PC Monitor HDMI Out
         ↓
    [HDMI Splitter] (optional, keep monitor connected)
         ↓
    [HDMI to USB-C adapter]
         ↓
    [Jetson USB-C port]
```

Test capture:
```bash
# On Jetson
v4l2-ctl --list-devices
# Should show /dev/video0 or /dev/video1
```

### Step 3: Wire Raspberry Pi Pico

**Connections:**
```
Jetson GPIO ─ Pico GPIO
──────────────────────
Pin 8 (TX)  → Pin 1 (RX)
Pin 10 (RX) → Pin 2 (TX)
GND         → GND
5V          → VBUS (or external power)
```

**Or USB Serial (easier):**
- Plug Pico into Jetson via USB
- Appears as `/dev/ttyACM0`
- No wiring needed

### Step 4: Flash Pico Firmware

```bash
# On Jetson
git clone https://github.com/gogosoto/chaos-bot.git
cd chaos-bot
python3 scripts/flash_pico.py
```

This installs CircuitPython + HID library on Pico.

### Step 5: Install Jetson Libraries

```bash
cd chaos-bot
pip install -r requirements-jetson.txt

# Download ML models
python3 scripts/download_models.py

# Test everything
python3 src/main.py --test-hardware
```

### Step 6: Assemble Enclosure

**Option A: 3D Print**
```bash
# Download case from Thingiverse (search "Jetson Nano case")
# Print at 20% infill, PETG for durability
# Add ventilation slots
```

**Option B: Aluminum Enclosure**
- Hammond 1554 series ($35)
- Drill holes for Ethernet, power, USB
- Passive cooling sufficient for Nano

**Thermal Management:**
- Apply thermal pads under Jetson (5 W/mK)
- Ensure 2cm clearance above (convection)
- Fan optional if ambient < 25°C

### Step 7: Test End-to-End

```bash
# On Jetson
python3 src/main.py --headless

# On PC (same network)
curl http://jetson-ip:5000/api/state
# Should return live bot state

# Launch CoD on PC
# Should see aim assist working
```

## Network Setup

### Find Jetson IP

```bash
# Option 1: On Jetson
hostname -I

# Option 2: From PC
arp-scan --localnet | grep Jetson
```

### Access Web Dashboard

From any device on network:
```
http://<jetson-ip>:5000
```

### Firewall Configuration

```bash
# On Jetson
sudo ufw allow 5000/tcp
sudo ufw allow 22/tcp   # SSH (optional)
```

## Power Management

### Jetson Clocks

```bash
# Max performance (uses ~15W)
sudo jetson_clocks

# Check power
sudo tegrastats
# Monitor temperature — should stay < 70°C under load
```

### Thermal Monitoring

```bash
# Watch temperature in real-time
watch -n 1 'tegrastats | grep "temp"'
```

If throttling (temp > 85°C):
1. Add ventilation holes
2. Increase fan speed
3. Reduce inference FPS in config.ini
4. Upgrade to Jetson Xavier NX (lower power)

## Troubleshooting

### Video Capture Not Working

```bash
# Check USB device
lsusb | grep -i video

# Test with ffmpeg
ffmpeg -f v4l2 -list_formats all -i /dev/video0

# Debug permissions
sudo usermod -a -G video $USER
```

### Pico Not Detected

```bash
# Check serial connection
ls -la /dev/ttyACM*

# If missing, flash CircuitPython
python3 scripts/flash_pico.py --force
```

### Models Fail to Download

```bash
# Check internet
ping google.com

# Manual download
wget https://storage.googleapis.com/mediapipe/tasks/vision/pose_landmarker_lite.tflite
# Place in models/
```

### Performance Too Slow

**Profile the bottleneck:**
```bash
python3 src/main.py --profile
# Shows which stage is slowest (capture, pose, detect, etc)
```

**Optimize:**
- Reduce input resolution (1280x720 instead of 1920x1080)
- Disable YOLOv8 if pose alone is sufficient
- Use quantized models (int8 instead of fp32)

## Maintenance

### Weekly

```bash
# Clean dust from vents
# Check temperature under load
tegrastats
```

### Monthly

```bash
# Update JetPack
sudo apt update && sudo apt upgrade

# Update Chaos Bot
cd ~/chaos-bot
git pull origin main
pip install -r requirements-jetson.txt --upgrade
```

### Yearly

- Replace microSD (wear-leveling finite)
- Check thermal paste degradation

## Performance Baseline

**Expected on Jetson Orin Nano:**
- Screen capture: 60 FPS
- MediaPipe Pose: 50-60 FPS
- YOLOv8-Nano: 40-50 FPS
- Mouse control: 60 FPS
- **End-to-end latency: 50-70ms** (capture → inference → aim → HID)

For comparison:
- RPi 4B: 30-40ms latency, lower FPS with ML
- Jetson Xavier NX: similar to Nano, lower power

## Next Steps

1. Order parts (~$341)
2. Follow assembly steps
3. Test with `--test-hardware`
4. Run against CoD
5. Tune HSV bounds for your monitor/setup

Questions? Open an issue on GitHub.
