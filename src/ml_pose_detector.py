"""
ML-powered pose detection using MediaPipe.
Detects standing/crouching/prone with confidence scores.
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class MLPoseDetector:
    """MediaPipe-based pose detection for Jetson."""

    def __init__(self, model_path='models/pose_landmarker_lite.tflite', gpu=True):
        """Initialize MediaPipe Pose."""
        self.model_path = model_path
        self.gpu = gpu

        # Setup base options
        if gpu:
            delegate = python.BaseOptions.Delegate.GPU
        else:
            delegate = python.BaseOptions.Delegate.CPU

        base_options = python.BaseOptions(
            model_asset_path=model_path,
            delegate=delegate
        )

        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
            num_poses=1  # Single pose detection
        )

        self.detector = vision.PoseLandmarker.create_from_options(options)
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose

        # Pose classification thresholds (shoulder/hip ratios)
        self.standing_threshold = 1.2    # Shoulders higher than hips
        self.crouching_threshold = 0.7   # Moderate compression
        self.prone_threshold = 0.4       # Very compressed

    def detect(self, frame):
        """
        Detect pose in frame.
        Returns: (pose_data, confidence)
          - pose_data: {
              'pose': 'standing'|'crouching'|'prone'|'unknown',
              'keypoints': [...],  # 33 landmarks
              'confidence': float,  # 0.0-1.0
            }
        """
        h, w = frame.shape[:2]

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect pose
        detection_result = self.detector.detect(mp_image)

        if not detection_result.landmarks or len(detection_result.landmarks) == 0:
            return {
                'pose': 'unknown',
                'keypoints': [],
                'confidence': 0.0
            }

        # Extract landmarks (33 keypoints)
        landmarks = detection_result.landmarks[0]
        keypoints = [(lm.x * w, lm.y * h, lm.z) for lm in landmarks]

        # Calculate pose classification
        pose, pose_confidence = self._classify_pose(landmarks)

        # Calculate overall confidence (average visibility)
        visibility = np.mean([lm.presence for lm in landmarks])

        return {
            'pose': pose,
            'keypoints': keypoints,
            'confidence': visibility,
            'pose_confidence': pose_confidence
        }

    def _classify_pose(self, landmarks):
        """
        Classify pose based on shoulder/hip ratio.
        Returns: (pose_type, confidence)
        """
        # Landmarks indices
        LEFT_SHOULDER = 11
        RIGHT_SHOULDER = 12
        LEFT_HIP = 23
        RIGHT_HIP = 24

        if not all(
            landmarks[idx].presence > 0.5
            for idx in [LEFT_SHOULDER, RIGHT_SHOULDER, LEFT_HIP, RIGHT_HIP]
        ):
            return 'unknown', 0.0

        # Calculate average positions
        shoulder_y = (landmarks[LEFT_SHOULDER].y + landmarks[RIGHT_SHOULDER].y) / 2
        hip_y = (landmarks[LEFT_HIP].y + landmarks[RIGHT_HIP].y) / 2

        # Calculate shoulder width (for normalization)
        shoulder_width = abs(
            landmarks[LEFT_SHOULDER].x - landmarks[RIGHT_SHOULDER].x
        )

        # Calculate vertical compression ratio
        # Higher ratio = more compressed (more crouched/prone)
        vertical_span = abs(shoulder_y - hip_y)
        if vertical_span == 0:
            ratio = 0
        else:
            ratio = shoulder_width / vertical_span

        # Classify
        if ratio > self.standing_threshold:
            return 'standing', 0.9
        elif ratio > self.crouching_threshold:
            return 'crouching', 0.8
        elif ratio > self.prone_threshold:
            return 'prone', 0.7
        else:
            return 'unknown', 0.5

    def draw_pose(self, frame, pose_data):
        """Draw pose landmarks on frame (for debugging)."""
        if not pose_data['keypoints']:
            return frame

        # Draw circles for each keypoint
        for kp in pose_data['keypoints']:
            x, y = int(kp[0]), int(kp[1])
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

        # Draw text
        cv2.putText(
            frame,
            f"{pose_data['pose']} ({pose_data['confidence']:.2f})",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        return frame


class AdaptiveColorLearner:
    """Learn enemy outline color during game intro."""

    def __init__(self, warmup_frames=30):
        self.warmup_frames = warmup_frames
        self.frame_count = 0
        self.color_history = []
        self.learned_bounds = None

    def update(self, frame, pose_data):
        """
        Update color learning based on detected pose.
        Returns: (learned_lower_bound, learned_upper_bound) or None if still warming up
        """
        if self.frame_count < self.warmup_frames:
            self.frame_count += 1

            # Sample pixels around detected pose
            if pose_data['keypoints']:
                hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                for kp in pose_data['keypoints']:
                    x, y = int(kp[0]), int(kp[1])
                    if 0 <= y < hsv_frame.shape[0] and 0 <= x < hsv_frame.shape[1]:
                        color = hsv_frame[y, x]
                        self.color_history.append(color)

            if self.frame_count == self.warmup_frames:
                # Compute learned bounds
                if self.color_history:
                    colors = np.array(self.color_history)
                    lower = np.percentile(colors, 5, axis=0)
                    upper = np.percentile(colors, 95, axis=0)
                    self.learned_bounds = (lower, upper)
                    return self.learned_bounds

        return self.learned_bounds

    def reset(self):
        """Reset for next map."""
        self.frame_count = 0
        self.color_history = []
        self.learned_bounds = None
