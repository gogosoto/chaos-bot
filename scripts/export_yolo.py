#!/usr/bin/env python3
"""
Export YOLOv11-nano to fastest inference format for the current platform.
Run once after install: python scripts/export_yolo.py

  Jetson Orin Nano Super  → TensorRT INT8 engine (~5 min)
  Dell CachyOS (RTX A2000) → TensorRT x86_64 engine
  Mac M1                   → CoreML (.mlpackage)
  Other Linux CPU          → skip (run .pt directly)
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from platform_utils import device_label, is_jetson, is_mac_m1, is_cuda_linux

MODEL_PT  = "models/yolo11n.pt"
MODEL_ENG = "models/yolo11n.engine"
MODEL_CML = "models/yolo11n.mlpackage"


def main():
    if not os.path.exists(MODEL_PT):
        print(f"ERROR: {MODEL_PT} not found.")
        print("Download it first:")
        print("  python -c \"from ultralytics import YOLO; YOLO('yolo11n.pt')\"")
        print("  mv yolo11n.pt models/")
        sys.exit(1)

    label = device_label()
    print(f"Platform: {label}")

    from ultralytics import YOLO
    model = YOLO(MODEL_PT)

    if label in ('jetson', 'cuda-linux'):
        if os.path.exists(MODEL_ENG):
            print(f"TensorRT engine already exists: {MODEL_ENG}")
            return
        print("Exporting to TensorRT INT8 engine (~5 minutes on first run)...")
        model.export(format="engine", int8=True, device=0)
        # ultralytics writes yolo11n.engine next to the .pt file; move it
        src = "yolo11n.engine"
        if os.path.exists(src):
            os.rename(src, MODEL_ENG)
        print(f"Done: {MODEL_ENG}" if os.path.exists(MODEL_ENG) else
              f"WARNING: engine not at expected path — check ultralytics output")

    elif label == 'mac-m1':
        if os.path.exists(MODEL_CML):
            print(f"CoreML model already exists: {MODEL_CML}")
            return
        print("Exporting to CoreML for Mac M1...")
        model.export(format="coreml")
        # ultralytics may write to CWD — move into models/
        src = "yolo11n.mlpackage"
        if os.path.exists(src):
            os.rename(src, MODEL_CML)
        print(f"Done: {MODEL_CML}" if os.path.exists(MODEL_CML) else
              f"WARNING: mlpackage not at expected path — check ultralytics output")

    else:
        print("CPU-only Linux: no export needed, running .pt directly.")
        print(f"Using: {MODEL_PT}")


if __name__ == "__main__":
    main()
