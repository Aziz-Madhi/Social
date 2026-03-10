#!/usr/bin/env python3
import os
import random
import re
from slideshow_tool import process_slide

BASE_DIR = "/Users/azizmadhi/Apps/Social"
HOOKS_DIR = os.path.join(BASE_DIR, "raw_images", "hook2")
SLIDES_DIR = os.path.join(BASE_DIR, "raw_images", "slides")
DEMOS_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "mood")
OUTPUT_ROOT = os.path.join(BASE_DIR, "ready_to_post")

HOOK_TITLE = "Physical symptoms I didn’t realize were actually caused by anxiety"
HOOK_SUBTITLE = "(and how my therapist taught me to deal with them.)"
ASPECT_RATIO = "3:4"

SIZES = {
    # Hook sizing tuned closer to the provided reference
    "cover_title": 44,
    "cover_subtitle": 30,
    "content": 45,
    "cover_subtitle_max_width_ratio": 0.85,
    "cover_subtitle_gap": 0.25,
}


def build_pools():
    hooks = list_images(HOOKS_DIR)
    slides = list_images(SLIDES_DIR)
    demos = list_images(DEMOS_DIR)

    if not hooks or not slides or not demos:
        raise RuntimeError("Missing images in hooks/slides/demos")

    random.shuffle(hooks)
    random.shuffle(slides)
    random.shuffle(demos)
    return {"hooks": hooks, "slides": slides, "demos": demos}


def pop_or_random(pool, folder):
    if pool:
        return pool.pop()
    return pick_one(folder)


def take_or_random(pool, folder, n):
    if len(pool) >= n:
        picked = pool[:n]
        del pool[:n]
        return picked
    return pick_many(folder, n)


def list_images(folder):
    valid = (".jpg", ".jpeg", ".png", ".webp")
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if not f.startswith(".") and f.lower().endswith(valid)
    ]


def pick_one(folder):
    imgs = list_images(folder)
    if not imgs:
        raise RuntimeError(f"No images found in {folder}")
    return random.choice(imgs)


def pick_many(folder, n):
    imgs = list_images(folder)
    if not imgs:
        raise RuntimeError(f"No images found in {folder}")
    if n <= len(imgs):
        return random.sample(imgs, n)
    return [random.choice(imgs) for _ in range(n)]


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:40]


number_re = re.compile(r"^\s*\d+\.?\s*")


def normalize_title(title):
    cleaned = number_re.sub("", title or "").strip()
    if not cleaned.startswith("-"):
        cleaned = f"- {cleaned}"
    return cleaned


def save_slideshow(index, title, slides, pools):
    folder_name = f"show_{index:02d}_{slugify(title)}"
    out_dir = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(out_dir, exist_ok=True)

    hook_image = pop_or_random(pools["hooks"], HOOKS_DIR)
    demo_image = pop_or_random(pools["demos"], DEMOS_DIR)
    slide_images = take_or_random(pools["slides"], SLIDES_DIR, len(slides) - 2)

    image_sequence = [hook_image] + slide_images + [demo_image]

    for i, (img_path, slide) in enumerate(zip(image_sequence, slides), 1):
        output_path = os.path.join(out_dir, f"slide_{i:02d}.jpg")
        process_slide(
            img_path,
            output_path,
            slide["type"],
            slide["texts"],
            aspect_ratio=ASPECT_RATIO,
            sizes=SIZES,
        )


def make_cover():
    return {
        "type": "cover",
        "texts": {"title": HOOK_TITLE, "subtitle": HOOK_SUBTITLE},
    }


def prefix_dash(text):
    text = text or ""
    text = text.strip()
    if not text.startswith(("-", "–", "—")):
        return f"- {text}"
    return text


def make_content(title, body, reality=None):
    return {
        "type": "content",
        "texts": {
            "title": prefix_dash(normalize_title(title)),
            "body": prefix_dash(body),
            "reality": prefix_dash(reality) if reality else reality,
        },
    }


slideshows = [
    (
        "Physical symptoms I didn’t realize were actually caused by anxiety",
        [
            make_cover(),
            make_content(
                "Shoulder tension that never left",
                "My shoulders lived up by my ears, tight as a rock. I blamed my desk chair and bad posture.",
                "The reality: My body was \"carrying\" the weight of stress I refused to acknowledge emotionally.",
            ),
            make_content(
                "2. Random nausea",
                "My stomach would turn before certain conversations or events. I thought I just had a \"nervous stomach.\"",
                "The reality: It was emotional rejection or fear manifesting physically. I couldn\"t \"digest\" the situation.",
            ),
            make_content(
                "3. Heavy chest feeling",
                "It felt like someone was sitting on my chest quietly. I’d tell myself \"I\"m fine\" and keep pushing through.",
                "The reality: Emotions don\"t vanish. If you don\"t cry them out, they sit on your chest.",
            ),
            make_content(
                "4. Constant on-edge energy",
                "Even on good days, I felt sharp, jumpy, and tense. I thought it was just my personality type.",
                "The reality: My nervous system was waiting for the next shoe to drop.",
            ),
            make_content(
                "5. What helped",
                "I started expressing emotions daily instead of storing them. I use Nafsy to vent and name the feeling in real time. My body actually relaxes when my feelings are finally heard.",
                None,
            ),
        ],
    ),
    (
        "My anxiety made me people-please",
        [
            make_cover(),
            make_content(
                "Saying yes automatically",
                "I’d agree to plans before I even checked if I had the energy. I thought I was just being helpful and easygoing.",
                "The reality: I was terrified that people would stop liking me if I wasn\"t useful to them.",
            ),
            make_content(
                "2. Apologizing too much",
                "I’d say sorry for things that weren’t my fault (or for just existing). I told myself it was just being polite.",
                "The reality: I was trying to shrink myself to avoid conflict or upsetting anyone.",
            ),
            make_content(
                "3. Avoiding boundaries",
                "I knew what I needed, but I couldn't say it out loud. I thought boundaries would make me \"difficult\" or \"high maintenance.\"",
                "The reality: Conflict felt dangerous to me. I thought a \"no\" would end the relationship.",
            ),
            make_content(
                "4. Overgiving to feel safe",
                "I’d go above and beyond just to feel secure in my connections. I called it loyalty.",
                "The reality: It was anxiety trying to \"buy\" safety and love through effort.",
            ),
            make_content(
                "5. What helped",
                "I reflect after situations using Nafsy. I ask: “Did I say yes because I wanted to, or because I was scared?” That awareness made setting boundaries feel less like a threat.",
                None,
            ),
        ],
    ),
    (
        "High functioning anxiety signs",
        [
            make_cover(),
            make_content(
                "Staying busy to avoid feelings",
                "If I stopped moving, the thoughts would catch up to me. I thought I was just hardworking and driven.",
                "The reality: I was using productivity as a numbing agent to avoid sitting with myself.",
            ),
            make_content(
                "2. Rest guilt",
                "Relaxing felt like a waste of time or a moral failing. I told myself I had big goals to reach.",
                "The reality: My nervous system viewed stillness as a threat, not a break.",
            ),
            make_content(
                "3. Always being “fine”",
                "I’d smile and say \"I'm good!\" on autopilot. I thought I was just a private person.",
                "The reality: I didn't feel safe enough to be vulnerable. I was performing wellness.",
            ),
            make_content(
                "4. A mind that never stops",
                "Even when I looked calm, my brain was running 100 mph. I assumed that's just how everyone thinks.",
                "The reality: It was anxiety keeping me hyper-vigilant, scanning for problems to solve.",
            ),
            make_content(
                "5. What helped",
                "I do two check-ins a day on Nafsy. It’s a small habit, but it forces me to drop the mask and be honest. The more I name the anxiety, the less it drives the bus.",
                None,
            ),
        ],
    ),
    (
        "Habits that secretly made my anxiety worse",
        [
            make_cover(),
            make_content(
                "Doomscrolling at night",
                "I’d end the day scrolling through bad news and perfect lives. I thought it helped me \"zone out\" and shut off.",
                "The reality: It was feeding my brain fear and comparison right before sleep.",
            ),
            make_content(
                "2. Skipping meals",
                "I’d forget to eat and wonder why I felt shaky and panicked. I told myself I was just \"in the zone.\"",
                "The reality: A blood sugar crash mimics a panic attack. My body thought we were in famine mode.",
            ),
            make_content(
                "3. Avoiding hard conversations",
                "I’d put off difficult talks to feel temporary relief. I thought I was choosing peace.",
                "The reality: Avoidance is interest on a debt. The anxiety grew bigger every day I waited.",
            ),
            make_content(
                "4. Bottling emotions",
                "I’d suppress my frustration until I eventually exploded. I thought bottling it up was \"being strong.\"",
                "The reality: Unspoken feelings build internal pressure. You can't heal what you don't feel.",
            ),
            make_content(
                "5. What helped",
                "I started venting daily on Nafsy and tracking my mood. It made the random spikes predictable (e.g., \"I'm anxious because I'm hungry\"). Awareness gave me control back.",
                None,
            ),
        ],
    ),
    (
        "Anxiety thoughts I believed (but shouldn’t have)",
        [
            make_cover(),
            make_content(
                "“If I don’t fix it now, it’ll get worse.”",
                "Everything felt urgent, like a 5-alarm fire. I thought urgency meant importance.",
                "The reality: Anxiety destroys your sense of time. Most things are not emergencies.",
            ),
            make_content(
                "2. “They’re mad at me.”",
                "One short text message would ruin my whole day. I’d assume I did something wrong.",
                "The reality: My brain was filling in the blanks with my biggest fears. They were just busy.",
            ),
            make_content(
                "3. “I can’t handle this.”",
                "I’d feel overwhelmed and accept defeat immediately. I forgot that I’ve survived 100% of my bad days.",
                "The reality: Anxiety shrinks your confidence to make the problem look bigger than it is.",
            ),
            make_content(
                "4. “I’m behind.”",
                "I compared my Chapter 1 to everyone else’s Chapter 20. I thought guilt was good motivation.",
                "The reality: \"Being behind\" is a myth. That was just fear dressed up as pressure.",
            ),
            make_content(
                "5. What helped",
                "I write the thought down, then log the actual feeling in Nafsy. Seeing it written out makes it look less convincing. It helps me separate the fear from the facts.",
                None,
            ),
        ],
    ),
    (
        "Tiny grounding tricks that actually worked",
        [
            make_cover(),
            make_content(
                "Name 5 things I see",
                "I force my eyes to find objects in the room. My brain wants to time-travel to a disastrous future.",
                "The fix: This forces me back to the present. I am here, and I am safe.",
            ),
            make_content(
                "2. Unclench my jaw",
                "I scan my body like I’m checking a car dashboard. I'm usually clenching my teeth or raising my shoulders without noticing.",
                "The fix: Physically letting go sends a signal to the brain that the \"threat\" isn't real.",
            ),
            make_content(
                "3. One long exhale",
                "Not a deep breath, but a slow, extended release (like blowing through a straw). It’s like hitting a reset button.",
                "The fix: The exhale activates the parasympathetic nervous system. It slows the heart rate down.",
            ),
            make_content(
                "4. Put a feeling into words",
                "Even if it’s messy: \"I feel scared\" or \"I feel overwhelmed.\" When it stays in my head, it feels like a monster.",
                "The fix: Naming it shrinks it. As Dan Siegel says, \"Name it to tame it.\"",
            ),
            make_content(
                "5. What helped most",
                "I open Nafsy, do a quick check-in, and vent it out. Don’t wait for your body to panic before you listen to it. Small daily releases prevent the big explosion.",
                None,
            ),
        ],
    ),
]


def main():
    pools = build_pools()
    for idx, (title, slides) in enumerate(slideshows, 1):
        save_slideshow(idx, title, slides, pools)
    print("All slideshows generated.")


if __name__ == "__main__":
    main()
