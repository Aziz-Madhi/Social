#!/usr/bin/env python3
"""
Slideshow Image Tool
Creates cover slides and content slides with proper text positioning.
"""

from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

def crop_to_aspect_ratio(img, target_ratio):
    """Center crop image to target aspect ratio (width:height as float)."""
    width, height = img.size
    current_ratio = width / height

    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        left = (width - new_width) // 2
        img = img.crop((left, 0, left + new_width, height))
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        top = (height - new_height) // 2
        img = img.crop((0, top, width, top + new_height))

    return img

# Font path - TikTok Sans from fonts folder
FONT_PATH = "/Users/azizmadhi/Apps/Social/fonts/TikTokSans-VariableFont_opsz,slnt,wdth,wght.ttf"

DEFAULT_FONT_AXES = {
    "opsz": 36,
    "wdth": 100,
    "wght": 600,
    "slnt": 0,
}

DEFAULT_SIZES = {
    "cover_title": 65,
    "cover_subtitle": 45,
    "content": 45,
}

def get_font(size, variation=None):
    """Load TikTok Sans font at specified size with a variable-font configuration."""
    try:
        font = ImageFont.truetype(FONT_PATH, size)
        if variation and variation.get("name"):
            font.set_variation_by_name(variation["name"])
        else:
            axes = dict(DEFAULT_FONT_AXES)
            if variation:
                axes.update({k: v for k, v in variation.items() if v is not None})
            # Axes order in file: opsz, wdth, wght, slnt
            font.set_variation_by_axes([axes["opsz"], axes["wdth"], axes["wght"], axes["slnt"]])
        return font
    except Exception as e:
        print(f"Warning: Could not set TikTok Sans variation: {e}")
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except Exception:
            return ImageFont.load_default()

def draw_text_with_stroke(draw, position, text, font, fill="white", stroke_width=2, stroke_fill="black"):
    """Draw text with subtle outline stroke for visibility."""
    x, y = position
    draw.text((x, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width."""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def create_cover_slide(img, title, subtitle=None, font_axes=None, sizes=None, text_position="center", stroke_config=None):
    """
    Create a cover/hook slide with title and optional subtitle.

    text_position: "top", "center", or "bottom"
    stroke_config: dict with "width", "color", "fill" keys
    """
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Font sizes - HOOK slide is BIGGER to grab attention
    scale = width / 1080
    sizes = sizes or DEFAULT_SIZES
    title_size = round(sizes.get("cover_title", 65) * scale)
    subtitle_size = round(sizes.get("cover_subtitle", 45) * scale)

    # Stroke settings
    stroke_config = stroke_config or {}
    stroke_width = stroke_config.get("width", 2)
    stroke_fill = stroke_config.get("color", "black")
    text_fill = stroke_config.get("fill", "white")

    title_font = get_font(title_size, font_axes)
    subtitle_font = get_font(subtitle_size, font_axes)

    # Max width for text
    max_text_width = int(width * sizes.get("cover_title_max_width_ratio", 0.85))
    subtitle_max_width = int(width * sizes.get("cover_subtitle_max_width_ratio", 0.8))

    # Wrap title
    title_lines = wrap_text(title, title_font, max_text_width, draw)

    # Calculate title block height
    line_height = title_size + 10
    title_block_height = len(title_lines) * line_height

    # Calculate total text block height
    total_text_height = title_block_height
    if subtitle:
        subtitle_lines_temp = wrap_text(subtitle, subtitle_font, subtitle_max_width, draw)
        sub_line_height = subtitle_size + 8
        total_text_height += int(title_size * sizes.get("cover_subtitle_gap", 0.5)) + len(subtitle_lines_temp) * sub_line_height

    # Position text block based on text_position
    margin_ratio = sizes.get("top_margin_ratio", 0.1)
    margin = int(height * margin_ratio)
    if text_position == "top":
        start_y = margin
    elif text_position == "bottom":
        start_y = height - total_text_height - margin
    else:  # center (default)
        start_y = (height - total_text_height) // 2

    title_align = sizes.get("cover_title_align", "center")
    subtitle_align = sizes.get("cover_subtitle_align", "center")
    title_left_ratio = sizes.get("cover_title_left_ratio", 0.1)
    subtitle_left_ratio = sizes.get("cover_subtitle_left_ratio", 0.1)

    # Draw title lines
    current_y = start_y
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        if title_align == "left":
            x = int(width * title_left_ratio)
        else:
            x = (width - text_width) // 2
        draw_text_with_stroke(draw, (x, current_y), line, title_font, fill=text_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        current_y += line_height

    # Draw subtitle if provided
    if subtitle:
        current_y += int(title_size * sizes.get("cover_subtitle_gap", 0.5))
        subtitle_lines = wrap_text(subtitle, subtitle_font, subtitle_max_width, draw)
        sub_line_height = subtitle_size + 8

        for line in subtitle_lines:
            bbox = draw.textbbox((0, 0), line, font=subtitle_font)
            text_width = bbox[2] - bbox[0]
            if subtitle_align == "left":
                x = int(width * subtitle_left_ratio)
            else:
                x = (width - text_width) // 2
            draw_text_with_stroke(draw, (x, current_y), line, subtitle_font, fill=text_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
            current_y += sub_line_height

    return img

def create_content_slide(img, title, body, reality_text=None, font_axes=None, sizes=None, text_position="center", stroke_config=None):
    """
    Create a content slide with title and body text.
    Optionally includes a "The reality:" section.

    text_position: "top", "center", or "bottom"
    stroke_config: dict with "width", "color", "fill" keys
    """
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Font sizes - ALL SAME SIZE (uniform like reference)
    scale = width / 1080
    sizes = sizes or DEFAULT_SIZES
    title_size = round(sizes.get("content", 45) * scale)
    body_size = round(sizes.get("content", 45) * scale)

    # Stroke settings
    stroke_config = stroke_config or {}
    stroke_width = stroke_config.get("width", 2)
    stroke_fill = stroke_config.get("color", "black")
    text_fill = stroke_config.get("fill", "white")

    # Spacing settings
    title_body_gap = sizes.get("title_body_gap", 0.8)
    body_reality_gap = sizes.get("body_reality_gap", 0.8)

    title_font = get_font(title_size, font_axes)
    body_font = get_font(body_size, font_axes)

    # Max width for text
    max_text_width = int(width * sizes.get("content_max_width_ratio", 0.85))

    # Prepare all text blocks
    title_lines = wrap_text(title, title_font, max_text_width, draw)
    body_lines = wrap_text(body, body_font, max_text_width, draw)
    reality_lines = wrap_text(reality_text, body_font, max_text_width, draw) if reality_text else []

    # Calculate total height
    title_line_height = title_size + 12
    body_line_height = body_size + 10

    total_height = (
        len(title_lines) * title_line_height +
        int(title_size * title_body_gap) +
        len(body_lines) * body_line_height
    )

    if reality_lines:
        total_height += int(body_size * body_reality_gap) + len(reality_lines) * body_line_height

    # Position text block based on text_position
    margin_ratio = sizes.get("top_margin_ratio", 0.1)
    margin = int(height * margin_ratio)
    if text_position == "top":
        start_y = margin
    elif text_position == "bottom":
        start_y = height - total_height - margin
    else:  # center (default)
        start_y = (height - total_height) // 2

    current_y = start_y

    # Draw title
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw_text_with_stroke(draw, (x, current_y), line, title_font, fill=text_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        current_y += title_line_height

    # Gap after title
    current_y += int(title_size * title_body_gap)

    # Draw body
    for line in body_lines:
        bbox = draw.textbbox((0, 0), line, font=body_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw_text_with_stroke(draw, (x, current_y), line, body_font, fill=text_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        current_y += body_line_height

    # Draw reality section if provided
    if reality_lines:
        current_y += int(body_size * body_reality_gap)
        for line in reality_lines:
            bbox = draw.textbbox((0, 0), line, font=body_font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw_text_with_stroke(draw, (x, current_y), line, body_font, fill=text_fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
            current_y += body_line_height

    return img

def render_slide(input_path, slide_type, texts, aspect_ratio="3:4", font_axes=None, sizes=None, text_position="center", stroke_config=None, min_width=1080):
    """
    Render a single slide and return a PIL Image.

    slide_type: "cover" or "content"
    texts: dict with keys depending on type
        - cover: {"title": str, "subtitle": str (optional)}
        - content: {"title": str, "body": str, "reality": str (optional)}
    text_position: "top", "center", or "bottom"
    stroke_config: dict with "width", "color", "fill" keys
    min_width: minimum output width in pixels
    """
    # Parse aspect ratio
    w, h = map(int, aspect_ratio.split(":"))
    ratio = w / h

    # Load image
    img = Image.open(input_path)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # Crop to aspect ratio
    img = crop_to_aspect_ratio(img, ratio)

    # Upscale to minimum resolution for crisp text
    min_height = int(min_width / ratio)
    if img.size[0] < min_width or img.size[1] < min_height:
        # Use LANCZOS for high-quality upscaling
        img = img.resize((min_width, min_height), Image.LANCZOS)

    # Apply text based on slide type
    if slide_type == "cover":
        img = create_cover_slide(
            img,
            texts.get("title", ""),
            texts.get("subtitle"),
            font_axes=font_axes,
            sizes=sizes,
            text_position=text_position,
            stroke_config=stroke_config,
        )
    else:
        img = create_content_slide(
            img,
            texts.get("title", ""),
            texts.get("body", ""),
            texts.get("reality"),
            font_axes=font_axes,
            sizes=sizes,
            text_position=text_position,
            stroke_config=stroke_config,
        )

    return img

def process_slide(input_path, output_path, slide_type, texts, aspect_ratio="3:4", font_axes=None, sizes=None, text_position="center", stroke_config=None, min_width=1080, jpeg_quality=100, jpeg_subsampling=0):
    """
    Process a single slide.

    slide_type: "cover" or "content"
    texts: dict with keys depending on type
        - cover: {"title": str, "subtitle": str (optional)}
        - content: {"title": str, "body": str, "reality": str (optional)}
    text_position: "top", "center", or "bottom"
    stroke_config: dict with "width", "color", "fill" keys
    min_width: minimum output width in pixels
    jpeg_quality: JPEG quality (1-100)
    jpeg_subsampling: JPEG subsampling (0 = best quality)
    """
    img = render_slide(
        input_path,
        slide_type,
        texts,
        aspect_ratio=aspect_ratio,
        font_axes=font_axes,
        sizes=sizes,
        text_position=text_position,
        stroke_config=stroke_config,
        min_width=min_width,
    )

    # Save with configurable quality
    if output_path.lower().endswith('.png'):
        img.save(output_path, optimize=False)
    else:
        # JPEG: use configurable quality settings
        img.save(output_path, quality=jpeg_quality, subsampling=jpeg_subsampling)
    print(f"Saved: {output_path}")
    return output_path

if __name__ == "__main__":
    print("Slideshow tool loaded. Use process_slide() function.")
