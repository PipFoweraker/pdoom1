#!/usr/bin/env python3
"""
Generate placeholder cat images for different doom levels.
These are temporary placeholders until proper art is created.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# Cat image specs: 256x256px PNG with transparency
IMAGE_SIZE = (256, 256)

# Doom level variants with colors
VARIANTS = {
    "happy.png": {
        "doom_range": "0-20%",
        "bg_color": (100, 200, 100, 255),  # Green
        "text": "😸\nHappy\n(0-20%)",
    },
    "concerned.png": {
        "doom_range": "21-40%",
        "bg_color": (200, 200, 100, 255),  # Yellow
        "text": "😐\nConcerned\n(21-40%)",
    },
    "worried.png": {
        "doom_range": "41-60%",
        "bg_color": (255, 165, 0, 255),  # Orange
        "text": "😟\nWorried\n(41-60%)",
    },
    "distressed.png": {
        "doom_range": "61-80%",
        "bg_color": (255, 100, 100, 255),  # Red
        "text": "😰\nDistressed\n(61-80%)",
    },
    "corrupted.png": {
        "doom_range": "81-100%",
        "bg_color": (150, 50, 200, 255),  # Purple/corrupted
        "text": "😱\nCorrupted\n(81-100%)",
    },
}


def create_placeholder_cat(filename: str, bg_color: tuple, text: str, output_dir: str):
    """Create a simple placeholder cat image"""
    # Create image with transparency
    img = Image.new("RGBA", IMAGE_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw a rounded square background
    margin = 20
    draw.rounded_rectangle(
        [(margin, margin), (IMAGE_SIZE[0] - margin, IMAGE_SIZE[1] - margin)],
        radius=30,
        fill=bg_color,
    )

    # Add text in center
    # Try to use a decent font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 32)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw centered text (no need to calculate text_x, text_y when using anchor='mm')
    draw.multiline_text(
        (IMAGE_SIZE[0] // 2, IMAGE_SIZE[1] // 2),
        text,
        fill=(0, 0, 0, 255),
        font=font,
        anchor="mm",
        align="center",
    )

    # Add "PLACEHOLDER" watermark
    watermark = "PLACEHOLDER"
    watermark_bbox = draw.textbbox((0, 0), watermark, font=small_font)
    watermark_width = watermark_bbox[2] - watermark_bbox[0]
    draw.text(
        ((IMAGE_SIZE[0] - watermark_width) // 2, IMAGE_SIZE[1] - 30),
        watermark,
        fill=(0, 0, 0, 128),
        font=small_font,
    )

    # Save
    output_path = os.path.join(output_dir, filename)
    img.save(output_path, "PNG")
    print(f"✓ Created: {output_path}")


def main():
    # Get script directory and navigate to cat assets directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, "godot", "assets", "cats", "default")

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("Generating placeholder cat images...")
    print(f"Output directory: {output_dir}")
    print()

    # Generate each variant
    for filename, config in VARIANTS.items():
        create_placeholder_cat(
            filename=filename,
            bg_color=config["bg_color"],
            text=config["text"],
            output_dir=output_dir,
        )

    print()
    print("✓ All placeholder images created!")
    print(f"  Location: {output_dir}")
    print()
    print("Note: These are temporary placeholders. Replace with proper art assets later.")


if __name__ == "__main__":
    main()
