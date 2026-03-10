#!/usr/bin/env python3
"""
Unified Slideshow Generator

Reads configuration from config.json and content from content.json.
Generates slideshows with configurable styling.

Usage:
    python generate.py                    # Use default config.json and content.json
    python generate.py -c my_config.json  # Use custom config file
    python generate.py -t my_content.json # Use custom content file
"""

import os
import json
import random
import re
import argparse
from slideshow_tool import process_slide

# Default file paths
DEFAULT_CONFIG = "config.json"
DEFAULT_CONTENT = "content.json"


def load_json(filepath):
    """Load and parse a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:50]


def prefix_dash(text: str) -> str:
    """Add leading dash if not present."""
    text = text or ""
    text = text.strip()
    if not text.startswith(("-", "–", "—")):
        return f"- {text}"
    return text


def list_images(folder):
    """Get all image files from a folder."""
    valid = (".jpg", ".jpeg", ".png", ".webp")
    if not os.path.exists(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if not f.startswith(".") and f.lower().endswith(valid)
    ]


def pick_random(folder):
    """Pick a random image from folder."""
    imgs = list_images(folder)
    if not imgs:
        raise RuntimeError(f"No images found in {folder}")
    return random.choice(imgs)


def pick_many_unique(folder, n):
    """Pick n unique images from folder."""
    imgs = list_images(folder)
    if not imgs:
        raise RuntimeError(f"No images found in {folder}")
    if n <= len(imgs):
        return random.sample(imgs, n)
    # Not enough uniques; fall back to sampling with replacement
    picked = imgs.copy()
    while len(picked) < n:
        picked.append(random.choice(imgs))
    random.shuffle(picked)
    return picked[:n]


def build_sizes_dict(config):
    """Build sizes dict from config for slideshow_tool."""
    font = config.get("font", {})
    max_width = config.get("max_width", {})
    spacing = config.get("spacing", {})

    return {
        "cover_title": font.get("cover_title", 50),
        "cover_subtitle": font.get("cover_subtitle", 38),
        "content": font.get("content", 45),
        "cover_title_max_width_ratio": max_width.get("cover_title", 0.85),
        "cover_subtitle_max_width_ratio": max_width.get("cover_subtitle", 0.82),
        "content_max_width_ratio": max_width.get("content", 0.85),
        "cover_subtitle_gap": spacing.get("cover_subtitle_gap", 0.35),
        "title_body_gap": spacing.get("title_body_gap", 0.8),
        "body_reality_gap": spacing.get("body_reality_gap", 0.8),
    }


def build_font_axes(config):
    """Build font axes dict from config."""
    font = config.get("font", {})
    return {
        "opsz": font.get("optical_size", 36),
        "wdth": font.get("width", 100),
        "wght": font.get("weight", 600),
        "slnt": font.get("slant", 0),
    }


def build_stroke_config(config):
    """Build stroke config dict from config."""
    stroke = config.get("stroke", {})
    return {
        "width": stroke.get("width", 2),
        "color": stroke.get("color", "black"),
        "fill": stroke.get("fill", "white"),
    }


def generate_slideshows(config, content):
    """Generate all slideshows from config and content."""
    # Get folder paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    folders = config.get("folders", {})
    hooks_dir = os.path.join(base_dir, folders.get("hooks", "raw_images/hooks"))
    slides_dir = os.path.join(base_dir, folders.get("slides", "raw_images/slides"))
    demo_dir = os.path.join(base_dir, folders.get("demo", "raw_images/demos/mood"))
    output_dir = os.path.join(base_dir, folders.get("output", "ready_to_post"))

    # Verify folders exist
    for folder, name in [(hooks_dir, "hooks"), (slides_dir, "slides"), (demo_dir, "demo")]:
        if not os.path.isdir(folder):
            raise RuntimeError(f"Missing folder: {folder}")
    os.makedirs(output_dir, exist_ok=True)

    # Build settings
    sizes = build_sizes_dict(config)
    font_axes = build_font_axes(config)
    stroke_config = build_stroke_config(config)
    text_position = config.get("text_position", "center")
    aspect_ratio = config.get("aspect_ratio", "3:4")

    # Output quality settings
    quality = config.get("output_quality", {})
    min_width = quality.get("min_width", 1080)
    jpeg_quality = quality.get("jpeg_quality", 100)
    jpeg_subsampling = quality.get("subsampling", 0)

    # Get hook content
    hook = content.get("hook", {})
    hook_title = hook.get("title", "")
    hook_subtitle = hook.get("subtitle", "")

    # Process each slideshow
    slideshows = content.get("slideshows", [])
    for idx, show in enumerate(slideshows, 1):
        name = show.get("name", f"slideshow_{idx}")
        slides = show.get("slides", [])

        # Create output folder
        show_dir = os.path.join(output_dir, f"show_{idx:02d}_{slugify(name)}")
        os.makedirs(show_dir, exist_ok=True)

        # Assign images
        num_content_slides = len(slides)
        hook_img = pick_random(hooks_dir)
        content_imgs = pick_many_unique(slides_dir, num_content_slides - 1)  # All but last
        demo_img = pick_random(demo_dir)

        # Process hook slide (slide 1)
        output_path = os.path.join(show_dir, "slide_01.jpg")
        process_slide(
            hook_img,
            output_path,
            "cover",
            {"title": hook_title, "subtitle": hook_subtitle},
            aspect_ratio=aspect_ratio,
            font_axes=font_axes,
            sizes=sizes,
            text_position=text_position,
            stroke_config=stroke_config,
            min_width=min_width,
            jpeg_quality=jpeg_quality,
            jpeg_subsampling=jpeg_subsampling,
        )

        # Process content slides (slides 2 to N-1)
        for i, slide in enumerate(slides[:-1]):
            output_path = os.path.join(show_dir, f"slide_{i+2:02d}.jpg")
            process_slide(
                content_imgs[i],
                output_path,
                "content",
                {
                    "title": prefix_dash(slide.get("title", "")),
                    "body": slide.get("body", ""),
                    "reality": slide.get("reality"),
                },
                aspect_ratio=aspect_ratio,
                font_axes=font_axes,
                sizes=sizes,
                text_position=text_position,
                stroke_config=stroke_config,
                min_width=min_width,
                jpeg_quality=jpeg_quality,
                jpeg_subsampling=jpeg_subsampling,
            )

        # Process demo slide (last slide)
        last_slide = slides[-1]
        output_path = os.path.join(show_dir, f"slide_{len(slides)+1:02d}.jpg")
        process_slide(
            demo_img,
            output_path,
            "content",
            {
                "title": prefix_dash(last_slide.get("title", "")),
                "body": last_slide.get("body", ""),
                "reality": last_slide.get("reality"),
            },
            aspect_ratio=aspect_ratio,
            font_axes=font_axes,
            sizes=sizes,
            text_position=text_position,
            stroke_config=stroke_config,
            min_width=min_width,
            jpeg_quality=jpeg_quality,
            jpeg_subsampling=jpeg_subsampling,
        )

    print(f"\nGenerated {len(slideshows)} slideshows into {output_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Generate slideshows from config and content files")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG, help="Path to config JSON file")
    parser.add_argument("-t", "--content", default=DEFAULT_CONTENT, help="Path to content JSON file")
    args = parser.parse_args()

    # Load files
    config = load_json(args.config)
    content = load_json(args.content)

    # Generate
    random.seed()  # Ensure randomness
    generate_slideshows(config, content)


if __name__ == "__main__":
    main()
