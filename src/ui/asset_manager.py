"""
Asset loading utilities for P(Doom) game assets.

Handles loading and caching of background images, icons, and other visual assets.
"""

import pygame
import os
from typing import Optional, Dict, Tuple


class AssetManager:
    """Manages loading and caching of game assets."""
    
    def __init__(self):
        self._image_cache: Dict[str, pygame.Surface] = {}
        self.assets_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'images')
    
    def load_image(self, filename: str, size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """
        Load an image from the assets directory.
        
        Args:
            filename: Name of the image file
            size: Optional (width, height) to scale the image
            
        Returns:
            pygame.Surface or None if loading fails
        """
        cache_key = f"{filename}_{size}" if size else filename
        
        if cache_key in self._image_cache:
            return self._image_cache[cache_key]
        
        try:
            filepath = os.path.join(self.assets_path, filename)
            if not os.path.exists(filepath):
                print(f"Asset not found: {filepath}")
                return None
                
            image = pygame.image.load(filepath)
            
            if size:
                image = pygame.transform.scale(image, size)
            
            # Convert for better performance
            if image.get_alpha() is not None:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            self._image_cache[cache_key] = image
            return image
            
        except pygame.error as e:
            print(f"Failed to load image {filename}: {e}")
            return None
    
    def get_background_image(self, name: str, screen_size: Tuple[int, int]) -> Optional[pygame.Surface]:
        """
        Get a background image scaled to screen size.
        
        Args:
            name: Name identifier for the background
            screen_size: (width, height) of the screen
            
        Returns:
            Scaled background image or None
        """
        filename_map = {
            'cat_throne': '20250915_0948_Doom\'s Cat Throne_simple_compose_01k559ztmqefybe80mbvyqgyvd.png',
            'office_inferno': '20250915_0952_Ominous Office Inferno_remix_01k55a6bc5fkxbq4txbwr8f61m.png',
            'doom_cat': 'small doom caat.png'
        }
        
        filename = filename_map.get(name)
        if not filename:
            print(f"Unknown background: {name}")
            return None
            
        return self.load_image(filename, screen_size)


# Global asset manager instance
asset_manager = AssetManager()


def draw_text_with_background(screen: pygame.Surface, text: str, font: pygame.font.Font, 
                            pos: Tuple[int, int], text_color: Tuple[int, int, int] = (255, 255, 255),
                            bg_color: Tuple[int, int, int, int] = (0, 0, 0, 128), 
                            padding: int = 10) -> pygame.Rect:
    """
    Draw text with a semi-transparent background for better visibility.
    
    Args:
        screen: Surface to draw on
        text: Text to render
        font: Font to use
        pos: (x, y) position for the text
        text_color: RGB color for the text
        bg_color: RGBA color for the background (includes alpha)
        padding: Padding around the text
        
    Returns:
        Rectangle area that was drawn
    """
    # Render the text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = pos
    
    # Create background rectangle with padding
    bg_rect = pygame.Rect(
        text_rect.x - padding,
        text_rect.y - padding,
        text_rect.width + 2 * padding,
        text_rect.height + 2 * padding
    )
    
    # Draw semi-transparent background
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surface.fill(bg_color)
    screen.blit(bg_surface, bg_rect.topleft)
    
    # Draw the text on top
    screen.blit(text_surface, text_rect.topleft)
    
    return bg_rect
