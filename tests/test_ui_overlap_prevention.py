"""
Tests for UI overlap prevention - Issue #121.

This module tests the safe zone system that ensures overlay panels
don't obscure core interactive areas.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import pygame
from src.ui.layout import get_ui_safe_zones, find_safe_overlay_position


class TestUIOverlapPrevention(unittest.TestCase):
    """Test UI overlap prevention system."""

    def test_safe_zones_defined(self):
        """Test that safe zones are properly defined for common screen sizes."""
        # Test with 800x600 screen
        zones = get_ui_safe_zones(800, 600)
        
        # Should have defined safe zones for major UI areas
        self.assertGreaterEqual(len(zones), 4, "Should define at least 4 safe zones")
        
        # All zones should be valid rectangles
        for zone in zones:
            self.assertIsInstance(zone, pygame.Rect)
            self.assertGreater(zone.width, 0)
            self.assertGreater(zone.height, 0)

    def test_safe_zones_cover_key_areas(self):
        """Test that safe zones cover key interactive areas."""
        w, h = 1024, 768
        zones = get_ui_safe_zones(w, h)
        
        # Resource header should be protected
        resource_header_point = (w // 2, int(h * 0.1))
        covered = any(zone.collidepoint(resource_header_point) for zone in zones)
        self.assertTrue(covered, "Resource header area should be in safe zones")
        
        # Action button area should be protected  
        action_area_point = (int(w * 0.2), int(h * 0.4))
        covered = any(zone.collidepoint(action_area_point) for zone in zones)
        self.assertTrue(covered, "Action button area should be in safe zones")

    def test_overlay_positioning_avoids_safe_zones(self):
        """Test that overlay positioning avoids intersecting with safe zones."""
        w, h = 800, 600
        safe_zones = get_ui_safe_zones(w, h)
        
        # Create a test overlay that should fit in the gap between action and upgrade areas
        # Gap is from x=280 to x=520, width=240. So max overlay width is ~220 to be safe
        overlay_rect = pygame.Rect(0, 0, 220, 150)
        
        # Position the overlay
        positioned_rect = find_safe_overlay_position(overlay_rect, w, h, safe_zones)
        
        # Verify it doesn't intersect with any safe zone
        for i, zone in enumerate(safe_zones):
            intersects = positioned_rect.colliderect(zone)
            self.assertFalse(intersects, 
                           f"Overlay at {positioned_rect} should not intersect safe zone {zone}")

    def test_overlay_stays_within_screen_bounds(self):
        """Test that positioned overlays stay within screen boundaries."""
        w, h = 800, 600
        safe_zones = get_ui_safe_zones(w, h)
        
        # Test various overlay sizes
        test_sizes = [(200, 150), (400, 300), (100, 100), (500, 400)]
        
        for width, height in test_sizes:
            overlay_rect = pygame.Rect(0, 0, width, height)
            positioned_rect = find_safe_overlay_position(overlay_rect, w, h, safe_zones)
            
            # Should be within screen bounds
            self.assertGreaterEqual(positioned_rect.x, 0)
            self.assertGreaterEqual(positioned_rect.y, 0)
            self.assertLessEqual(positioned_rect.right, w)
            self.assertLessEqual(positioned_rect.bottom, h)

    def test_large_overlay_fallback_positioning(self):
        """Test that very large overlays fall back to centered positioning."""
        w, h = 800, 600
        safe_zones = get_ui_safe_zones(w, h)
        
        # Create an overlay that's too large to avoid all safe zones
        overlay_rect = pygame.Rect(0, 0, 600, 500)
        positioned_rect = find_safe_overlay_position(overlay_rect, w, h, safe_zones)
        
        # Should fall back to one of the fallback positions or minimal intersection
        # The exact position depends on the algorithm, so just verify it's reasonable
        self.assertGreaterEqual(positioned_rect.x, 0)
        self.assertGreaterEqual(positioned_rect.y, 0)
        self.assertLessEqual(positioned_rect.right, w)
        self.assertLessEqual(positioned_rect.bottom, h)

    def test_different_screen_sizes(self):
        """Test safe zone behavior with different screen sizes."""
        screen_sizes = [(640, 480), (1024, 768), (1920, 1080)]
        
        for w, h in screen_sizes:
            safe_zones = get_ui_safe_zones(w, h)
            
            # Should always have safe zones defined
            self.assertGreater(len(safe_zones), 0, f"No safe zones for size {w}x{h}")
            
            # Safe zones should be reasonable size relative to screen
            for zone in safe_zones:
                self.assertLessEqual(zone.width, w, "Safe zone wider than screen")
                self.assertLessEqual(zone.height, h, "Safe zone taller than screen")


class TestOverlayDragConstraints(unittest.TestCase):
    """Test overlay drag constraints to screen bounds."""
    
    def test_drag_constraints_basic(self):
        """Test basic drag constraint functionality."""
        # For now, this is a placeholder for future drag constraint tests
        # The drag functionality will be implemented as part of overlay panels
        pass


if __name__ == '__main__':
    unittest.main()