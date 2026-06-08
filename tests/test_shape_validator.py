"""
Unit tests for shape_validator.py — geometric validation and pose detection.
"""
import unittest
import numpy as np
import cv2
import sys
import os

# Add src to path so we can import shape_validator
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from shape_validator import ShapeValidator


class MockConfig:
    """Mock config object for testing."""
    def __init__(self):
        # Shape validation defaults
        self.shape_validation_enabled = True
        self.check_aspect_ratio = True
        self.aspect_ratio_min = 0.3
        self.aspect_ratio_max = 0.8
        self.check_area_threshold = True
        self.min_blob_area = 20
        self.max_blob_area = 50000
        self.check_convexity = True
        self.min_convexity_score = 0.3
        self.check_solidity = True
        self.min_solidity_score = 0.5
        self.check_vertical_bias = True
        self.vertical_bias_threshold = 0.8

        # Pose detection defaults
        self.pose_standing_threshold = 1.2
        self.pose_crouching_threshold = 0.7
        self.pose_prone_threshold = 0.4
        self.pose_lead_standing = 0.4
        self.pose_lead_crouching = 0.5
        self.pose_lead_prone = 0.6


class TestShapeValidator(unittest.TestCase):
    """Test suite for ShapeValidator."""

    def setUp(self):
        self.config = MockConfig()
        self.validator = ShapeValidator(self.config)

    def _create_rectangle_contour(self, width, height):
        """Helper: create a rectangular contour (human-like standing)."""
        rect = np.array([
            [[0, 0]],
            [[width, 0]],
            [[width, height]],
            [[0, height]]
        ], dtype=np.int32)
        return rect

    def _create_circle_contour(self, radius):
        """Helper: create a circular contour."""
        circle = cv2.ellipse2Poly(
            (radius, radius),
            (radius, radius),
            0,
            0,
            360,
            1
        ).astype(np.int32).reshape(-1, 1, 2)
        return circle

    # --- Aspect Ratio Tests ---
    def test_aspect_ratio_standing(self):
        """Tall narrow contour (standing): should pass."""
        # 50 wide × 100 tall = aspect 2.0 (tall)
        contour = self._create_rectangle_contour(50, 100)
        result = self.validator._check_aspect_ratio(contour)
        self.assertTrue(result, "Standing posture (tall/narrow) should pass aspect ratio check")

    def test_aspect_ratio_prone(self):
        """Wide flat contour (prone): should fail."""
        # 200 wide × 50 tall = aspect 0.25 (wide)
        contour = self._create_rectangle_contour(200, 50)
        result = self.validator._check_aspect_ratio(contour)
        self.assertFalse(result, "Prone posture (wide/flat) should fail aspect ratio check")

    # --- Area Threshold Tests ---
    def test_area_too_small(self):
        """Tiny contour (noise): should fail."""
        contour = self._create_rectangle_contour(2, 2)  # area = 4 pixels
        result = self.validator._check_area_threshold(contour)
        self.assertFalse(result, "Noise (tiny area) should fail threshold check")

    def test_area_valid(self):
        """Medium contour: should pass."""
        contour = self._create_rectangle_contour(50, 100)  # area = 5000 pixels
        result = self.validator._check_area_threshold(contour)
        self.assertTrue(result, "Valid size should pass area threshold")

    def test_area_too_large(self):
        """Massive contour (skybox): should fail."""
        contour = self._create_rectangle_contour(500, 500)  # area = 250k pixels
        result = self.validator._check_area_threshold(contour)
        self.assertFalse(result, "Massive object should fail area threshold")

    # --- Convexity Tests ---
    def test_convexity_circle(self):
        """Perfect circle: high convexity, should pass."""
        contour = self._create_circle_contour(30)
        result = self.validator._check_convexity(contour)
        self.assertTrue(result, "Smooth circle should pass convexity check")

    def test_convexity_rectangle(self):
        """Rectangle: moderate convexity, should pass."""
        contour = self._create_rectangle_contour(50, 100)
        result = self.validator._check_convexity(contour)
        self.assertTrue(result, "Rectangle should pass convexity check")

    # --- Solidity Tests ---
    def test_solidity_solid_rectangle(self):
        """Solid filled rectangle: high solidity, should pass."""
        contour = self._create_rectangle_contour(50, 100)
        result = self.validator._check_solidity(contour)
        self.assertTrue(result, "Solid rectangle should pass solidity check")

    # --- Pose Detection Tests ---
    def test_pose_standing(self):
        """Tall narrow contour: should detect as standing."""
        contour = self._create_rectangle_contour(40, 120)
        pose, confidence = self.validator.detect_pose(contour)
        self.assertEqual(pose, "standing", "Tall narrow shape should be detected as standing")
        self.assertGreater(confidence, 0.5, "Confidence should be reasonable")

    def test_pose_crouching(self):
        """Medium aspect ratio: should detect as crouching."""
        contour = self._create_rectangle_contour(70, 70)
        pose, confidence = self.validator.detect_pose(contour)
        self.assertEqual(pose, "crouching", "Medium aspect ratio should be crouching")

    def test_pose_prone(self):
        """Wide flat contour: should detect as prone."""
        contour = self._create_rectangle_contour(150, 60)
        pose, confidence = self.validator.detect_pose(contour)
        self.assertEqual(pose, "prone", "Wide flat shape should be detected as prone")
        self.assertGreater(confidence, 0.5, "Confidence should be reasonable")

    # --- Aim Lead Tests ---
    def test_aim_lead_standing(self):
        """Standing pose: aim lead should be at chest."""
        lead = self.validator.get_aim_lead_for_pose("standing")
        self.assertEqual(lead, self.config.pose_lead_standing)
        self.assertLess(lead, 0.5, "Standing aim should be higher (< 0.5)")

    def test_aim_lead_prone(self):
        """Prone pose: aim lead should be at center."""
        lead = self.validator.get_aim_lead_for_pose("prone")
        self.assertEqual(lead, self.config.pose_lead_prone)
        self.assertGreater(lead, 0.5, "Prone aim should be lower (> 0.5)")

    # --- Validation Chain Tests ---
    def test_is_valid_target_human_like(self):
        """Valid human-like shape: should pass all checks."""
        contour = self._create_rectangle_contour(50, 100)
        result = self.validator.is_valid_target(contour)
        self.assertTrue(result, "Human-like contour should pass validation")

    def test_is_valid_target_too_small(self):
        """Tiny contour: should fail validation."""
        contour = self._create_rectangle_contour(2, 2)
        result = self.validator.is_valid_target(contour)
        self.assertFalse(result, "Noise should fail validation")

    def test_is_valid_target_disabled(self):
        """When validation disabled: all contours pass."""
        self.config.shape_validation_enabled = False
        self.validator = ShapeValidator(self.config)
        contour = self._create_rectangle_contour(2, 2)
        result = self.validator.is_valid_target(contour)
        self.assertTrue(result, "All contours should pass when validation disabled")


if __name__ == '__main__':
    unittest.main()
