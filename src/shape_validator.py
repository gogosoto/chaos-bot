"""
    Unibot, an open-source colorbot.
    Copyright (C) 2025 vike256

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import cv2
import numpy as np


class ShapeValidator:
    """Geometric heuristics to filter false positives, validate human-like shapes, and detect pose."""

    def __init__(self, config):
        self.cfg = config
        self.last_detected_pose = None  # Cache last pose for smoothing

    def is_valid_target(self, contour):
        """
        Check if a contour matches human-like shape criteria.
        Returns True if contour passes all enabled filters.
        """
        if not self.cfg.shape_validation_enabled:
            return True

        if len(contour) < 5:  # Need minimum points for ellipse/convex hull
            return False

        # Check each heuristic
        if self.cfg.check_aspect_ratio and not self._check_aspect_ratio(contour):
            return False

        if self.cfg.check_area_threshold and not self._check_area_threshold(contour):
            return False

        if self.cfg.check_convexity and not self._check_convexity(contour):
            return False

        if self.cfg.check_solidity and not self._check_solidity(contour):
            return False

        if self.cfg.check_vertical_bias and not self._check_vertical_bias(contour):
            return False

        return True

    def detect_pose(self, contour):
        """
        Detect player pose: 'standing', 'crouching', or 'prone'.
        Uses bounding box aspect ratio and height-to-width metrics.
        Returns pose string and confidence (0-1).
        """
        x, y, w, h = cv2.boundingRect(contour)

        if w == 0 or h == 0:
            return "unknown", 0.0

        # Aspect ratio: height / width
        aspect_ratio = h / w

        # Normalized height (relative to expected standing height)
        # Calibrate these thresholds per-game via config
        standing_threshold = self.cfg.pose_standing_threshold
        crouching_threshold = self.cfg.pose_crouching_threshold
        prone_threshold = self.cfg.pose_prone_threshold

        confidence = 0.0

        if aspect_ratio >= standing_threshold:
            # Tall, narrow shape = standing
            pose = "standing"
            confidence = min(1.0, (aspect_ratio - standing_threshold) / standing_threshold)
        elif aspect_ratio >= crouching_threshold:
            # Medium aspect ratio = crouching
            pose = "crouching"
            # Confidence based on distance from standing/prone thresholds
            confidence = 0.7
        else:
            # Low aspect ratio = prone (lying down, wide flat)
            pose = "prone"
            confidence = min(1.0, (crouching_threshold - aspect_ratio) / crouching_threshold)

        self.last_detected_pose = pose
        return pose, confidence

    def get_aim_lead_for_pose(self, pose):
        """
        Adjust aim lead (head height offset) based on detected pose.
        Standing: aim at chest/head
        Crouching: aim slightly lower
        Prone: aim at center mass (ground)
        """
        lead_map = {
            "standing": self.cfg.pose_lead_standing,
            "crouching": self.cfg.pose_lead_crouching,
            "prone": self.cfg.pose_lead_prone,
            "unknown": 0.5  # Default middle
        }
        return lead_map.get(pose, 0.5)

    def _check_aspect_ratio(self, contour):
        """
        Verify aspect ratio (width:height) is within human-like range.
        Humans are taller than wide. Range: 0.3 to 0.8 (h/w ratio).
        """
        x, y, w, h = cv2.boundingRect(contour)

        if w == 0:
            return False

        aspect_ratio = h / w

        # Allow tall thin shapes (humans) but not wide flat shapes (sky, walls)
        return self.cfg.aspect_ratio_min <= aspect_ratio <= self.cfg.aspect_ratio_max

    def _check_area_threshold(self, contour):
        """
        Filter out noise (too small) and massive objects (too large).
        """
        area = cv2.contourArea(contour)
        return self.cfg.min_blob_area <= area <= self.cfg.max_blob_area

    def _check_convexity(self, contour):
        """
        Measure how 'blobby' vs. 'spiky' the shape is.
        Human silhouettes are relatively smooth, not extremely irregular.
        Convexity score: 0-1, where 1 is perfect circle.
        """
        area = cv2.contourArea(contour)
        if area == 0:
            return False

        # Perimeter-based convexity: tighter = more regular
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return False

        # Circularity: 4π * area / perimeter²
        circularity = 4 * np.pi * area / (perimeter ** 2)

        # Allow somewhat irregular shapes (humans aren't circles)
        return circularity >= self.cfg.min_convexity_score

    def _check_solidity(self, contour):
        """
        Ratio of blob area to convex hull area.
        Humans are relatively solid (not fragmented).
        Solidity: 0-1, where 1 means perfectly filled convex shape.
        """
        area = cv2.contourArea(contour)
        if area == 0:
            return False

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)

        if hull_area == 0:
            return False

        solidity = area / hull_area
        return solidity >= self.cfg.min_solidity_score

    def _check_vertical_bias(self, contour):
        """
        Slight preference for shapes taller than wide.
        Penalizes horizontal blobs (clouds, landscapes).
        Not a hard filter—just skews scoring toward vertical.
        """
        x, y, w, h = cv2.boundingRect(contour)

        if w == 0:
            return False

        # Ratio of height to width. > 1.0 means taller than wide.
        height_to_width = h / w

        # Accept if reasonably vertical, or if within tolerance
        return height_to_width >= self.cfg.vertical_bias_threshold
