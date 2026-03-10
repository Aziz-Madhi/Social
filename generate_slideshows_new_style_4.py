#!/usr/bin/env python3
import json
import os
import random
import re
from typing import Dict, List, Sequence, Tuple

from slideshow_tool import process_slide

BASE_DIR = "/Users/azizmadhi/Apps/Social"
HOOKS_DIR = os.path.join(BASE_DIR, "NEW", "hooks")
SLIDES_DIR = os.path.join(BASE_DIR, "NEW", "slides")
OUTPUT_ROOT = os.path.join(BASE_DIR, "ready_to_post", "new_style_4")
ASPECT_RATIO = "3:4"

VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")

# Stronger text treatment than run_batch.py to match references.
SIZES = {
    "cover_title": 60,
    "cover_subtitle": 34,
    "content": 52,
    "cover_subtitle_gap": 0.35,
    "title_body_gap": 1.05,
    "body_reality_gap": 1.15,
    "cover_title_max_width_ratio": 0.88,
    "cover_subtitle_max_width_ratio": 0.62,
    "cover_subtitle_align": "left",
    "cover_subtitle_left_ratio": 0.24,
    "top_margin_ratio": 0.15,
    "content_max_width_ratio": 0.9,
}

HOOK_A_TITLE = "Physical symptoms I didn’t realize were actually caused by anxiety"
HOOK_A_SUBTITLE = "(and how My therapist taught me to deal with them.)"

HOOK_B_TITLE = "Weird body sensations I ignored that were actually my nervous system screaming for help."
HOOK_B_SUBTITLE = "(And the shift that finally calmed them down.)"


def list_images(folder: str) -> List[str]:
    return [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if not name.startswith(".") and name.lower().endswith(VALID_EXTENSIONS)
    ]


def validate_inputs(hooks: Sequence[str], slides: Sequence[str]) -> None:
    missing = [p for p in (HOOKS_DIR, SLIDES_DIR) if not os.path.isdir(p)]
    if missing:
        raise RuntimeError(
            "Missing required folder(s): " + ", ".join(missing)
        )
    if not hooks:
        raise RuntimeError(f"No images found in hooks folder: {HOOKS_DIR}")
    if not slides:
        raise RuntimeError(f"No images found in slides folder: {SLIDES_DIR}")


def build_pools(hooks: Sequence[str], slides: Sequence[str]) -> Dict[str, List[str]]:
    hook_pool = list(hooks)
    slide_pool = list(slides)
    random.shuffle(hook_pool)
    random.shuffle(slide_pool)
    return {"hooks": hook_pool, "slides": slide_pool}


def pop_or_random(pool: List[str], full_list: Sequence[str]) -> str:
    if pool:
        return pool.pop()
    return random.choice(list(full_list))


def take_unique_slides(pool: List[str], full_list: Sequence[str], count: int) -> List[str]:
    if len(pool) >= count:
        picked = pool[:count]
        del pool[:count]
        return picked
    full = list(full_list)
    if not full:
        raise RuntimeError("No slide images available for selection.")
    unique_pick_count = min(count, len(full))
    picked = random.sample(full, unique_pick_count)
    while len(picked) < count:
        picked.append(random.choice(full))
    return picked


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:64]


def assert_in_folder(path: str, folder: str) -> None:
    abs_path = os.path.abspath(path)
    abs_folder = os.path.abspath(folder)
    if not abs_path.startswith(abs_folder + os.sep):
        raise RuntimeError(f"Selected image outside allowed folder: {abs_path}")


def make_cover(title: str, subtitle: str) -> Dict[str, object]:
    return {"type": "cover", "texts": {"title": title, "subtitle": subtitle}}


def make_content(trigger_or_symptom: str, lie: str, reality: str) -> Dict[str, object]:
    return {
        "type": "content",
        "texts": {
            "title": trigger_or_symptom,
            "body": lie,
            "reality": reality,
        },
    }


def build_slideshows() -> List[Tuple[str, List[Dict[str, object]]]]:
    return [
        (
            "Physical Symptoms",
            [
                make_cover(HOOK_A_TITLE, HOOK_A_SUBTITLE),
                make_content(
                    "The Trigger: Bright fluorescent lights giving me a headache.",
                    'The Lie: "I\'m just tired."',
                    "The Reality: My brain couldn't filter the visual input. It felt like a physical attack on my nervous system because I couldn't shut it out.",
                ),
                make_content(
                    "The Trigger: Hearing three conversations at once and freezing up.",
                    'The Lie: "I\'m being rude/distracted."',
                    "The Reality: Auditory processing lag. I physically couldn't separate the voices from the background noise. It all became one loud wall of sound.",
                ),
                make_content(
                    'The Trigger: Clothes that feel "wrong" or tight on my skin.',
                    'The Lie: "I\'m just being picky."',
                    "The Reality: Tactile defensiveness. I started tracking my triggers in the Nafsy app and realized that when I'm anxious, my skin feels raw and unsafe, making every fabric feel like sandpaper.",
                ),
                make_content(
                    "The Trigger: Sudden, extreme exhaustion after 20 minutes out.",
                    'The Lie: "I\'m out of shape."',
                    "The Reality: My brain was burning 2x the energy just trying to regulate the environment. I wasn't tired; I was depleted.",
                ),
            ],
        ),
        (
            "Social Hangovers",
            [
                make_cover(HOOK_A_TITLE, HOOK_A_SUBTITLE),
                make_content(
                    "The Symptom: Complete physical exhaustion after socializing.",
                    'The Lie: "I\'m depressed."',
                    'The Reality: I spent the whole night "masking"—physically performing a version of myself to fit in. My body is tired from the performance.',
                ),
                make_content(
                    "The Symptom: A tight chest while replaying every conversation.",
                    'The Lie: "I\'m just reflecting."',
                    "The Reality: My anxiety was scanning the night for mistakes I might have made. I wasn't reflecting; I was punishing myself.",
                ),
                make_content(
                    "The Symptom: Irritability and snapping at family the next day.",
                    'The Lie: "Everyone is annoying me."',
                    "The Reality: My social battery was in the negatives. I used the Nafsy app to check in with my mood and saw the pattern: I didn't hate them; I was just overstimulated and needed silence to recharge.",
                ),
                make_content(
                    "The Symptom: Nausea or dread about the next event.",
                    'The Lie: "I hate people."',
                    "The Reality: I don't hate people; I hate how drained I feel afterwards. My body is trying to protect me from burnout.",
                ),
            ],
        ),
        (
            "Numbing and Dissociation",
            [
                make_cover(HOOK_B_TITLE, HOOK_B_SUBTITLE),
                make_content(
                    'The Symptom: Feeling physically "blank" or empty during tragedies.',
                    'The Lie: "I\'m heartless."',
                    "The Reality: My emotional circuit breaker tripped. The feelings were too big for my body to hold, so the system shut down to protect me.",
                ),
                make_content(
                    "The Symptom: Losing hours of time staring at a wall.",
                    'The Lie: "I\'m just bored."',
                    "The Reality: I was checking out of reality because being present in my body was too painful.",
                ),
                make_content(
                    "The Symptom: Feeling like I was floating outside my body (Movie Mode).",
                    'The Lie: "I\'m going crazy."',
                    "The Reality: Depersonalization. I logged this sensation in the Nafsy app and learned it’s a common anxiety symptom where you detach from your body when you feel unsafe.",
                ),
                make_content(
                    "The Symptom: Binge eating to feel something.",
                    'The Lie: "I\'m just hungry."',
                    "The Reality: I was trying to manually stimulate my nervous system to wake it up. I wasn't hungry for food; I was hungry for connection.",
                ),
            ],
        ),
        (
            "Nighttime Anxiety",
            [
                make_cover(HOOK_B_TITLE, HOOK_B_SUBTITLE),
                make_content(
                    "The Habit: Staying up until 2 AM even when eyes are burning.",
                    'The Lie: "I\'m just a night owl."',
                    'The Reality: "Revenge Bedtime Procrastination." I had no control over my day, so I physically forced my body to stay awake to steal time back.',
                ),
                make_content(
                    "The Habit: Heart racing the second the lights go out.",
                    'The Lie: "I\'m not tired anymore."',
                    "The Reality: The silence was too loud. Without distractions, the suppressed adrenaline from the day finally hit my bloodstream.",
                ),
                make_content(
                    "The Habit: Racing thoughts that feel like physical noise.",
                    'The Lie: "My brain is just active."',
                    "The Reality: I was ruminating. I started doing a 'Brain Dump' in the Nafsy app before bed, which helped me physically offload the worry so I didn't have to carry it into sleep.",
                ),
                make_content(
                    "The Habit: Waking up with a clenched jaw or sore shoulders.",
                    'The Lie: "I slept wrong."',
                    'The Reality: I was tense all night. My body never actually entered "rest and digest" mode; I was sleeping with one eye open.',
                ),
            ],
        ),
    ]


def save_slideshow(
    index: int,
    title: str,
    slides: List[Dict[str, object]],
    pools: Dict[str, List[str]],
    hooks_all: Sequence[str],
    slides_all: Sequence[str],
) -> None:
    folder_name = f"show_{index:02d}_{slugify(title)}"
    out_dir = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(out_dir, exist_ok=True)

    hook_image = pop_or_random(pools["hooks"], hooks_all)
    middle_images = take_unique_slides(pools["slides"], slides_all, 4)
    assert_in_folder(hook_image, HOOKS_DIR)
    for path in middle_images:
        assert_in_folder(path, SLIDES_DIR)
    image_sequence = [hook_image] + middle_images

    for i, (img_path, slide) in enumerate(zip(image_sequence, slides), start=1):
        output_path = os.path.join(out_dir, f"slide_{i:02d}.jpg")
        process_slide(
            img_path,
            output_path,
            slide["type"],
            slide["texts"],
            aspect_ratio=ASPECT_RATIO,
            sizes=SIZES,
            text_position="top" if slide["type"] == "cover" else "center",
        )

    # Source trace for quick validation.
    with open(os.path.join(out_dir, "selection.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "hooks_dir": HOOKS_DIR,
                "slides_dir": SLIDES_DIR,
                "hook_image": hook_image,
                "slide_images": middle_images,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )


def main() -> None:
    hooks_all = list_images(HOOKS_DIR) if os.path.isdir(HOOKS_DIR) else []
    slides_all = list_images(SLIDES_DIR) if os.path.isdir(SLIDES_DIR) else []
    validate_inputs(hooks_all, slides_all)

    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    pools = build_pools(hooks_all, slides_all)
    decks = build_slideshows()

    for idx, (title, slides) in enumerate(decks, start=1):
        save_slideshow(idx, title, slides, pools, hooks_all, slides_all)

    print(f"Generated {len(decks)} slideshows in {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
