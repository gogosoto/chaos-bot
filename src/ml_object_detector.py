"""
YOLOv11-nano object detection with platform-conditional backend selection.
Called only on small HSV-filtered ROI crops — not full frames.
"""

import cv2
import numpy as np

from platform_utils import device_label


class MLObjectDetector:
    """
    YOLOv11-nano detector with platform-conditional backend.

    Backends (selected automatically):
      jetson     → TensorRT .engine file (~5ms inference)
      cuda-linux → CUDA torch (~15ms, Dell RTX A2000)
      mac-m1     → MPS (~25ms)
      linux      → CPU (~80ms fallback)

    Called ONLY on small HSV-filtered ROI crops (not the full frame).
    """

    PERSON_CLASS = 0

    def __init__(self, model_path: str, confidence: float = 0.5):
        from ultralytics import YOLO
        self.confidence = confidence
        self._label = device_label()
        self.model = YOLO(model_path, task='detect')

        if self._label == 'jetson':
            pass  # TensorRT engine handles device placement internally
        elif self._label == 'cuda-linux':
            self.model.to('cuda')
        elif self._label == 'mac-m1':
            self.model.to('mps')
        else:
            self.model.to('cpu')

        print(f"[MLObjectDetector] backend={self._label} model={model_path}")

    def detect_in_crop(self, crop: np.ndarray) -> list[dict]:
        """
        Run detection on a small crop (HSV-filtered ROI).
        Returns list of dicts: {name, conf, bbox (x1,y1,x2,y2 as ndarray)}.
        """
        results = self.model.predict(source=crop, conf=self.confidence, verbose=False)
        detections = []
        for result in results:
            for box in result.boxes:
                if int(box.cls[0]) == self.PERSON_CLASS:
                    detections.append({
                        'name': 'person',
                        'conf': float(box.conf[0]),
                        'bbox': box.xyxy[0].cpu().numpy(),
                    })
        return detections

    def best_target_in_crop(self, crop: np.ndarray,
                             fov_center: tuple) -> tuple | None:
        """
        Detect in crop, return (dx, dy) offset from fov_center to nearest head.
        Returns None if no person confirmed.
        Head position = top 15% of bounding box.
        """
        detections = self.detect_in_crop(crop)
        if not detections:
            return None

        cx, cy = fov_center
        best, best_dist = None, float('inf')
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            head_x = int((x1 + x2) / 2)
            head_y = int(y1 + (y2 - y1) * 0.15)
            dist = ((head_x - cx) ** 2 + (head_y - cy) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best = (head_x - cx, head_y - cy)
        return best
