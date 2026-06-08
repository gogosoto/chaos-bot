"""
YOLOv8-Nano object detection for head/body identification.
GPU-accelerated inference on Jetson.
"""

import cv2
import numpy as np
from ultralytics import YOLO


class MLObjectDetector:
    """YOLOv8-Nano for enemy head/body detection."""

    def __init__(self, model_name='yolov8n.pt', confidence_threshold=0.5, gpu=True):
        """Initialize YOLOv8-Nano model."""
        self.confidence_threshold = confidence_threshold
        self.gpu = gpu

        # Load model
        self.model = YOLO(model_name)

        # Set to GPU if available
        if gpu:
            self.model.to('cuda')
        else:
            self.model.to('cpu')

        # Common object classes we care about (person, etc.)
        self.PERSON_CLASS = 0  # COCO dataset person class

    def detect(self, frame):
        """
        Detect objects in frame.
        Returns: {
          'detections': [
            {'class': int, 'name': str, 'conf': float, 'bbox': (x1, y1, x2, y2)},
            ...
          ],
          'inference_time_ms': float
        }
        """
        # Run inference
        results = self.model.predict(source=frame, conf=self.confidence_threshold, verbose=False)

        detections = []
        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                bbox = box.xyxy[0].cpu().numpy()

                # Only care about people
                if cls_id == self.PERSON_CLASS:
                    detections.append({
                        'class': cls_id,
                        'name': 'person',
                        'conf': confidence,
                        'bbox': bbox  # (x1, y1, x2, y2)
                    })

        return {
            'detections': detections,
            'inference_time_ms': result.speed.get('inference', 0)
        }

    def filter_by_region(self, detections, roi_rect):
        """
        Filter detections to only those inside ROI.
        roi_rect: (x, y, w, h) from screen.py
        """
        x, y, w, h = roi_rect
        filtered = []

        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2

            # Check if center is within ROI
            if x <= center_x <= x + w and y <= center_y <= y + h:
                filtered.append(det)

        return filtered

    def get_head_region(self, detection):
        """
        Extract head region from detection.
        Assumes typical person proportions: head is top 20% of bbox.
        Returns: (x1, y1, x2, y2) for head region
        """
        x1, y1, x2, y2 = detection['bbox']
        height = y2 - y1
        head_y2 = y1 + height * 0.25  # Top 25% is head

        return (x1, y1, x2, head_y2)

    def draw_detections(self, frame, detections, color=(0, 255, 0)):
        """Draw detection boxes on frame (for debugging)."""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{det['name']} {det['conf']:.2f}"
            cv2.putText(
                frame,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1
            )

        return frame


class HeadTracker:
    """Track detected heads across frames."""

    def __init__(self, max_distance=50):
        self.max_distance = max_distance
        self.tracked_heads = {}
        self.next_id = 0

    def update(self, detections):
        """
        Associate detections with tracked heads.
        Returns: list of (head_id, detection) tuples
        """
        tracked = []

        for det in detections:
            # Get head region
            x1, y1, x2, y2 = det['bbox']
            head_x = (x1 + x2) / 2
            head_y = y1  # Top of detection

            # Find nearest tracked head
            best_id = None
            best_distance = self.max_distance

            for track_id, prev_pos in self.tracked_heads.items():
                distance = np.sqrt((head_x - prev_pos[0])**2 + (head_y - prev_pos[1])**2)
                if distance < best_distance:
                    best_distance = distance
                    best_id = track_id

            # Assign to tracked head or create new
            if best_id is not None:
                self.tracked_heads[best_id] = (head_x, head_y)
                tracked.append((best_id, det))
            else:
                new_id = self.next_id
                self.next_id += 1
                self.tracked_heads[new_id] = (head_x, head_y)
                tracked.append((new_id, det))

        return tracked

    def reset(self):
        """Reset tracking for new map."""
        self.tracked_heads = {}
        self.next_id = 0
