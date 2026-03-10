#!/usr/bin/env python3
"""
Local UI server for the Social slideshow tool.
"""

import base64
import io
import os
import random
import time
from flask import Flask, jsonify, render_template, request

from slideshow_tool import render_slide, process_slide

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "raw_images")
HOOKS_DIR = os.path.join(RAW_DIR, "hooks")
SLIDES_DIR = os.path.join(RAW_DIR, "slides")
DEMOS_DIR = os.path.join(RAW_DIR, "demos")
OUTPUT_DIR = os.path.join(BASE_DIR, "ready_to_post")

app = Flask(__name__)


def list_images(folder_path, prefix):
    if not os.path.exists(folder_path):
        return []
    items = []
    for name in sorted(os.listdir(folder_path)):
        if name.startswith("."):
            continue
        lower = name.lower()
        if lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
            items.append(f"{prefix}/{name}")
    return items


def resolve_image_path(rel_path):
    if not rel_path:
        raise ValueError("Missing image path")
    abs_path = os.path.abspath(os.path.join(BASE_DIR, rel_path))
    if not abs_path.startswith(RAW_DIR + os.sep):
        raise ValueError("Invalid image path")
    if not os.path.exists(abs_path):
        raise ValueError("Image not found")
    return abs_path


def pick_random_image(folder_path):
    images = list_images(folder_path, os.path.relpath(folder_path, BASE_DIR))
    if not images:
        raise ValueError(f"No images found in {folder_path}")
    return resolve_image_path(random.choice(images))


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def build_image_sequence(slides, use_demo_image_for_last, image_opts):
    total = len(slides)
    if total == 0:
        return []

    random_hooks = bool(image_opts.get("randomHooks", True))
    random_slides = bool(image_opts.get("randomSlides", True))
    random_demos = bool(image_opts.get("randomDemos", True))

    selected_hook = image_opts.get("hookImage")
    selected_demo = image_opts.get("demoImage")
    selected_slides = image_opts.get("slideImages", [])

    if random_hooks:
        hook_path = pick_random_image(HOOKS_DIR)
    else:
        hook_path = resolve_image_path(selected_hook)

    if use_demo_image_for_last and total > 1:
        middle_count = total - 2
        use_demo = True
    else:
        middle_count = total - 1
        use_demo = False

    if middle_count > 0:
        if random_slides:
            slide_pool = list_images(SLIDES_DIR, "raw_images/slides")
            if not slide_pool:
                raise ValueError("No slide images found")
            if middle_count <= len(slide_pool):
                chosen = random.sample(slide_pool, middle_count)
            else:
                chosen = [random.choice(slide_pool) for _ in range(middle_count)]
            slide_paths = [resolve_image_path(p) for p in chosen]
        else:
            if len(selected_slides) < middle_count:
                raise ValueError("Not enough slide images selected")
            slide_paths = [resolve_image_path(p) for p in selected_slides[:middle_count]]
    else:
        slide_paths = []

    if use_demo:
        if random_demos:
            demo_path = pick_random_image(DEMOS_DIR)
        else:
            demo_path = resolve_image_path(selected_demo)
    else:
        demo_path = None

    sequence = [hook_path] + slide_paths
    if demo_path:
        sequence.append(demo_path)

    return sequence


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/images")
def api_images():
    return jsonify({
        "hooks": list_images(HOOKS_DIR, "raw_images/hooks"),
        "slides": list_images(SLIDES_DIR, "raw_images/slides"),
        "demos": list_images(DEMOS_DIR, "raw_images/demos"),
    })


@app.route("/api/preview", methods=["POST"])
def api_preview():
    data = request.get_json(force=True)

    rel_path = data.get("imagePath")
    folder = data.get("folder")
    if not rel_path:
        if folder == "hooks":
            abs_path = pick_random_image(HOOKS_DIR)
        elif folder == "slides":
            abs_path = pick_random_image(SLIDES_DIR)
        elif folder == "demos":
            abs_path = pick_random_image(DEMOS_DIR)
        else:
            return jsonify({"error": "Missing image selection"}), 400
    else:
        abs_path = resolve_image_path(rel_path)

    slide_type = data.get("slideType", "content")
    texts = data.get("texts", {})
    aspect_ratio = data.get("aspectRatio", "3:4")
    font_axes = data.get("fontAxes")
    sizes = data.get("sizes")

    try:
        img = render_slide(
            abs_path,
            slide_type,
            texts,
            aspect_ratio=aspect_ratio,
            font_axes=font_axes,
            sizes=sizes,
        )
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=90, subsampling=0)
        encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
        return jsonify({"dataUrl": f"data:image/jpeg;base64,{encoded}"})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/save", methods=["POST"])
def api_save():
    data = request.get_json(force=True)
    shows = data.get("shows", [])
    if not shows:
        return jsonify({"error": "No slideshows provided"}), 400

    options = data.get("options", {})
    image_opts = data.get("images", {})

    aspect_ratio = options.get("aspectRatio", "3:4")
    font_axes = options.get("fontAxes")
    sizes = options.get("sizes")
    use_demo_image_for_last = bool(options.get("useDemoImageForLast", True))

    ensure_output_dir()
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    results = []

    for show_index, show in enumerate(shows, 1):
        slides = show.get("slides", [])
        if not slides:
            continue

        image_sequence = build_image_sequence(slides, use_demo_image_for_last, image_opts)
        if len(image_sequence) != len(slides):
            return jsonify({"error": "Image count does not match slide count"}), 400

        saved = []
        for slide_index, (image_path, slide) in enumerate(zip(image_sequence, slides), 1):
            output_name = f"show_{show_index:02d}_{timestamp}_slide_{slide_index:02d}.jpg"
            output_path = os.path.join(OUTPUT_DIR, output_name)
            process_slide(
                image_path,
                output_path,
                slide.get("type", "content"),
                slide.get("texts", {}),
                aspect_ratio=aspect_ratio,
                font_axes=font_axes,
                sizes=sizes,
            )
            saved.append(output_name)

        results.append({"show": show_index, "slides": saved})

    return jsonify({"saved": results})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
