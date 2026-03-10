#!/usr/bin/env python3
"""
Simple Image Text Overlay Tool
Crops image to aspect ratio and overlays text with stroke for visibility.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def crop_to_aspect_ratio(img, target_ratio):
    """Center crop image to target aspect ratio (width:height as float)."""
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Image is wider than target - crop width
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    elif current_ratio < target_ratio:
        # Image is taller than target - crop height
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    return img

def add_text_overlay(img, text, font_path=None, font_size=None):
    """Add text with stroke to bottom-center of image."""
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Auto-size font based on image width if not specified
    if font_size is None:
        font_size = max(24, width // 20)

    # Load font
    try:
        if font_path and os.path.exists(font_path):
            font = ImageFont.truetype(font_path, font_size)
        else:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        font = ImageFont.load_default()

    # Calculate text position (bottom center with padding)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = height - text_height - (height // 10)  # 10% from bottom

    # Draw stroke (outline) for visibility
    stroke_width = max(2, font_size // 25)
    draw.text((x, y), text, font=font, fill="white", stroke_width=stroke_width, stroke_fill="black")

    return img

def process_image(input_path, output_path, caption_text, aspect_ratio="4:3"):
    """Main function to process a single image."""
    # Parse aspect ratio
    w, h = map(int, aspect_ratio.split(":"))
    ratio = w / h

    # Load and process
    img = Image.open(input_path)

    # Convert to RGB if necessary (for RGBA images)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img = crop_to_aspect_ratio(img, ratio)
    img = add_text_overlay(img, caption_text)

    # Save
    img.save(output_path, quality=95)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    # Example usage
    import sys
    if len(sys.argv) >= 4:
        process_image(sys.argv[1], sys.argv[2], sys.argv[3],
                     sys.argv[4] if len(sys.argv) > 4 else "4:3")
    else:
        print("Usage: python simple_tool.py <input> <output> <caption> [aspect_ratio]")
