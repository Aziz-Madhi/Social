#!/usr/bin/env python3
"""
Automated Slideshow Generator

Folder structure:
    raw_images/
    ├── hooks/     → First slide (hook image)
    ├── slides/    → Middle slides (content images)
    └── demos/     → Last slide (demo/app promo image)

The script automatically picks:
    - 1 image from hooks/ for the first slide
    - N images from slides/ for middle slides
    - 1 image from demos/ for the last slide
"""

import os
import random
from slideshow_tool import process_slide

# Folder paths
HOOKS_FOLDER = "raw_images/hooks"
SLIDES_FOLDER = "raw_images/slides"
DEMOS_FOLDER = "raw_images/demos"
OUTPUT_FOLDER = "ready_to_post"

def get_images_from_folder(folder_path):
    """Get all image files from a folder."""
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    images = []

    if os.path.exists(folder_path):
        for f in os.listdir(folder_path):
            if f.lower().endswith(valid_extensions) and not f.startswith('.'):
                images.append(os.path.join(folder_path, f))

    return images

def create_slideshow(slides_content, aspect_ratio="3:4", shuffle_slides=True):
    """
    Create a slideshow automatically from organized folders.

    Parameters:
        slides_content: list of dicts with slide content
            - First item: hook content {"title": "", "subtitle": ""}
            - Middle items: content slides {"title": "", "body": "", "reality": ""}
            - Last item: demo slide content
        aspect_ratio: str, default "3:4"
        shuffle_slides: bool, randomize image selection (default True)

    Returns:
        list of output file paths
    """
    # Get available images from each folder
    hook_images = get_images_from_folder(HOOKS_FOLDER)
    slide_images = get_images_from_folder(SLIDES_FOLDER)
    demo_images = get_images_from_folder(DEMOS_FOLDER)

    # Validate folders have images
    if not hook_images:
        raise ValueError(f"No images found in {HOOKS_FOLDER}/")
    if not slide_images:
        raise ValueError(f"No images found in {SLIDES_FOLDER}/")
    if not demo_images:
        raise ValueError(f"No images found in {DEMOS_FOLDER}/")

    # Calculate how many slides we need
    num_slides = len(slides_content)
    num_middle_slides = num_slides - 2  # Subtract hook and demo

    if num_middle_slides > len(slide_images):
        raise ValueError(f"Not enough images in {SLIDES_FOLDER}/. Need {num_middle_slides}, found {len(slide_images)}")

    # Shuffle if requested
    if shuffle_slides:
        random.shuffle(hook_images)
        random.shuffle(slide_images)
        random.shuffle(demo_images)

    # Assign images to slides
    assigned_images = []
    assigned_images.append(hook_images[0])  # First: hook
    assigned_images.extend(slide_images[:num_middle_slides])  # Middle: slides
    assigned_images.append(demo_images[0])  # Last: demo

    # Ensure output folder exists
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Process each slide
    output_files = []

    for i, (image_path, content) in enumerate(zip(assigned_images, slides_content), 1):
        output_path = f"{OUTPUT_FOLDER}/slide_{i:02d}.jpg"

        # Determine slide type
        if i == 1:
            slide_type = "cover"  # Hook
        else:
            slide_type = "content"  # Middle slides and demo

        process_slide(
            input_path=image_path,
            output_path=output_path,
            slide_type=slide_type,
            texts=content,
            aspect_ratio=aspect_ratio
        )

        output_files.append(output_path)

    print(f"\nSlideshow complete! {len(output_files)} slides created.")
    print(f"Images used:")
    print(f"  Hook:   {os.path.basename(assigned_images[0])}")
    for i, img in enumerate(assigned_images[1:-1], 2):
        print(f"  Slide {i}: {os.path.basename(img)}")
    print(f"  Demo:   {os.path.basename(assigned_images[-1])}")

    return output_files


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Define your slideshow content
    # First item = Hook, Middle items = Content, Last item = Demo

    slides = [
        # Slide 1: HOOK (from hooks/ folder)
        {
            "title": "I thought I was just shy",
            "subtitle": "It was social anxiety"
        },

        # Slide 2: CONTENT (from slides/ folder)
        {
            "title": "1. Planning my sentences",
            "body": "I'd rehearse my order or my greeting before I even walked in the door. I thought I was just quiet and thoughtful.",
            "reality": "The reality: I was trying to avoid the \"danger\" of embarrassment or stumbling over my words."
        },

        # Slide 3: CONTENT (from slides/ folder)
        {
            "title": "2. Feeling watched",
            "body": "I'd worry about my posture, my hands, and how I was standing. I assumed everyone was judging me as hard as I judged myself.",
            "reality": "The reality: Social anxiety makes you feel like you're constantly performing on a stage."
        },

        # Slide 4: CONTENT (from slides/ folder)
        {
            "title": "3. Needing an escape plan",
            "body": "I couldn't relax unless I knew exactly when and how I could leave. I told myself I was just being responsible with my time.",
            "reality": "The reality: It was claustrophobia. I needed to know I wasn't trapped in the discomfort."
        },

        # Slide 5: CONTENT (from slides/ folder)
        {
            "title": "4. Overanalyzing faces and tone",
            "body": "One \"off\" look from a friend would convince me they hated me. I told myself I was just observant.",
            "reality": "The reality: My brain was reading danger signals where there weren't any."
        },

        # Slide 6: DEMO (from demos/ folder)
        {
            "title": "5. What helped",
            "body": "I check in on Nafsy before and after social plans. It helps me label what I'm scared of (e.g., \"judgment\") not just feel the panic. Then I show up softer, not forced.",
            "reality": None
        },
    ]

    # Create the slideshow
    create_slideshow(slides, aspect_ratio="3:4")
