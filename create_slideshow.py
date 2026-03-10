#!/usr/bin/env python3
"""Create the social anxiety slideshow."""

from slideshow_tool import process_slide
import os

# Image assignments
images = [
    "raw_images/Give_us_another_2k_202601212216.jpeg",  # Slide 1 - Cover
    "raw_images/shower.jpeg",                            # Slide 2
    "raw_images/waterr.jpeg",                            # Slide 3
    "raw_images/#concert #livemusic.jpg",                # Slide 4
    "raw_images/Jay adore la musique 🎶.jpg",            # Slide 5
    "raw_images/ .jpg",                                  # Slide 6
]

# Slide content
slides = [
    {
        "type": "cover",
        "texts": {
            "title": "I thought I was just shy",
            "subtitle": "It was social anxiety"
        }
    },
    {
        "type": "content",
        "texts": {
            "title": "1. Planning my sentences",
            "body": "I'd rehearse my order or my greeting before I even walked in the door. I thought I was just quiet and thoughtful.",
            "reality": "The reality: I was trying to avoid the \"danger\" of embarrassment or stumbling over my words."
        }
    },
    {
        "type": "content",
        "texts": {
            "title": "2. Feeling watched",
            "body": "I'd worry about my posture, my hands, and how I was standing. I assumed everyone was judging me as hard as I judged myself.",
            "reality": "The reality: Social anxiety makes you feel like you're constantly performing on a stage."
        }
    },
    {
        "type": "content",
        "texts": {
            "title": "3. Needing an escape plan",
            "body": "I couldn't relax unless I knew exactly when and how I could leave. I told myself I was just being responsible with my time.",
            "reality": "The reality: It was claustrophobia. I needed to know I wasn't trapped in the discomfort."
        }
    },
    {
        "type": "content",
        "texts": {
            "title": "4. Overanalyzing faces and tone",
            "body": "One \"off\" look from a friend would convince me they hated me. I told myself I was just observant.",
            "reality": "The reality: My brain was reading danger signals where there weren't any."
        }
    },
    {
        "type": "content",
        "texts": {
            "title": "5. What helped",
            "body": "I check in on Nafsy before and after social plans. It helps me label what I'm scared of (e.g., \"judgment\") not just feel the panic. Then I show up softer, not forced.",
            "reality": None
        }
    },
]

# Process all slides
output_dir = "ready_to_post"
os.makedirs(output_dir, exist_ok=True)

for i, (image_path, slide) in enumerate(zip(images, slides), 1):
    output_path = f"{output_dir}/slide_{i:02d}.jpg"
    process_slide(
        image_path,
        output_path,
        slide["type"],
        slide["texts"],
        aspect_ratio="3:4"
    )

print("\nSlideshow complete!")
