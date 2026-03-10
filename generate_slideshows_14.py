#!/usr/bin/env python3
"""
Generate 14 anxiety-focused slideshows (IDs 21-34) using format #1.

Image rules:
- Slide 1 image: random from raw_images/hooks
- Slides 2-5 images: random from raw_images/slides (unique when possible)
- Slide 6 image: semantic routing from raw_images/demos/* based on slide 6 text
- Save each slideshow into ready_to_post/show_##_<slug>/slide_XX.jpg
"""

import os
import random
import re
from typing import Dict, List

from slideshow_tool import process_slide

BASE_DIR = "/Users/azizmadhi/Apps/Social"
HOOKS_DIR = os.path.join(BASE_DIR, "raw_images", "hooks")
SLIDES_DIR = os.path.join(BASE_DIR, "raw_images", "slides")
DEMO_MOOD_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "mood")
DEMO_YEAR_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "year view")
DEMO_CHAT_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "chat")
DEMO_EXERCISE_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "exercise")
OUTPUT_ROOT = os.path.join(BASE_DIR, "ready_to_post")
ASPECT_RATIO = "3:4"

DEMO_DIRS = [DEMO_MOOD_DIR, DEMO_YEAR_DIR, DEMO_CHAT_DIR, DEMO_EXERCISE_DIR]
VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp")

# Keep format #1 rendering style.
SIZES = {
    "cover_title": 50,
    "cover_subtitle": 38,
    "content": 45,
    "cover_subtitle_max_width_ratio": 0.82,
    "cover_subtitle_gap": 0.35,
}

number_re = re.compile(r"^\s*\d+\.?\s*")


DECKS = [
    {
        "id": 21,
        "title": "Why I refused to ask for help",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Habit: Doing everything myself, even when drowning.",
                "body": 'The Lie: "I just prefer working alone."',
                "reality": "The Reality: I didn't trust anyone to catch me if I fell. I learned early that I was the only reliable person.",
            },
            {
                "title": "The Habit: Hiding my struggles until they were resolved.",
                "body": 'The Lie: "I do not want to burden anyone."',
                "reality": "The Reality: Vulnerability felt dangerous. I thought showing weakness would make people leave.",
            },
            {
                "title": "The Habit: Resenting people who did ask for help.",
                "body": 'The Lie: "They are so needy."',
                "reality": "The Reality: It was envy. I wished I felt safe enough to be needy too.",
            },
            {
                "title": "The Habit: Rejecting compliments or support.",
                "body": 'The Lie: "I do not need charity."',
                "reality": "The Reality: Receiving care felt foreign and uncomfortable to my nervous system.",
            },
            {
                "title": "How I started letting people in",
                "body": "I realized independence is a trauma response, not a trophy. I started using Nafsy to admit when I was struggling, even if just to myself.",
                "reality": 'It was the first place I allowed myself to say, "I cannot carry this alone."',
            },
        ],
    },
    {
        "id": 22,
        "title": 'Scary thoughts I thought meant I was a "bad person"',
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": 'The Thought: "What if I just drove off this bridge?"',
                "body": 'The Lie: "I must be secretly suicidal."',
                "reality": "The Reality: It is a High Place Phenomenon. My brain was actually checking for danger, not desiring it.",
            },
            {
                "title": "The Thought: sudden violent images.",
                "body": 'The Lie: "I am a monster."',
                "reality": "The Reality: These are ego-dystonic thoughts. They disturb you because they are the opposite of who you are.",
            },
            {
                "title": 'The Thought: "What if I screamed right now?"',
                "body": 'The Lie: "I am losing my mind."',
                "reality": "The Reality: It is just anxiety testing the boundaries of your control.",
            },
            {
                "title": 'The Thought: "Did I leave the stove on?" (x20)',
                "body": 'The Lie: "I am forgetful."',
                "reality": "The Reality: My brain was looking for a concrete problem to solve because I felt internally chaotic.",
            },
            {
                "title": "What actually helped",
                "body": "Fighting the thoughts made them stickier. Now, I just log them in Nafsy without judging them.",
                "reality": "Seeing them written down takes the power away. It turns a monster into just a sentence.",
            },
        ],
    },
    {
        "id": 23,
        "title": "Why the grocery store made me want to cry",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Trigger: Bright fluorescent lights.",
                "body": 'The Lie: "I just have a headache."',
                "reality": "The Reality: My brain could not filter the visual input. It felt like an attack on my nervous system.",
            },
            {
                "title": "The Trigger: Multiple conversations happening at once.",
                "body": 'The Lie: "I am being rude or distracted."',
                "reality": "The Reality: My auditory processing was lagging. I physically could not separate the voices from the background noise.",
            },
            {
                "title": "The Trigger: Clothes that felt wrong or tight.",
                "body": 'The Lie: "I am just picky."',
                "reality": "The Reality: Tactile defensiveness. When I am anxious, my skin feels raw and unsafe.",
            },
            {
                "title": "The Trigger: Sudden exhaustion after 20 minutes.",
                "body": 'The Lie: "I am out of shape."',
                "reality": "The Reality: My brain was burning 2x the energy just trying to regulate the environment.",
            },
            {
                "title": "What actually helped",
                "body": "I stopped forcing myself to push through. I check Nafsy before I go out. If my battery is low, I wear headphones or order delivery.",
                "reality": "Honoring my limits is not weakness, it is maintenance.",
            },
        ],
    },
    {
        "id": 24,
        "title": "Why criticism felt like a physical punch",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Trigger: A slight change in someone's tone.",
                "body": 'The Lie: "They hate me."',
                "reality": "The Reality: I was hyper-vigilant. I was anticipating pain so I would not be blindsided.",
            },
            {
                "title": "The Trigger: constructive feedback at work.",
                "body": 'The Lie: "I am going to get fired."',
                "reality": "The Reality: Rejection Sensitive Dysphoria (RSD). My brain interprets correction as a threat to my safety.",
            },
            {
                "title": "The Trigger: Being left out of a plan.",
                "body": 'The Lie: "I am unlovable."',
                "reality": "The Reality: It triggered an old wound of abandonment. The pain was from the past, not the present.",
            },
            {
                "title": "The Trigger: Someone joking about me.",
                "body": 'The Lie: "I have no sense of humor."',
                "reality": "The Reality: Shame. I could not laugh because I was too busy wondering if the joke was true.",
            },
            {
                "title": "What actually helped",
                "body": "I had to learn to pause before reacting. I use Nafsy to fact check the feeling.",
                "reality": 'I ask: "Did they say they hate me? Or did they just ask me to wash a dish?" It grounds me.',
            },
        ],
    },
    {
        "id": 25,
        "title": "Why I tried to fix everyone's problems but my own",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Habit: Giving advice when no one asked.",
                "body": 'The Lie: "I am just helpful."',
                "reality": "The Reality: Other people's pain made me anxious. I was fixing them to soothe myself.",
            },
            {
                "title": "The Habit: Attracting projects not partners.",
                "body": 'The Lie: "I see their potential."',
                "reality": "The Reality: If I am focused on their mess, I do not have to look at mine.",
            },
            {
                "title": "The Habit: Feeling responsible for their moods.",
                "body": 'The Lie: "I am an empath."',
                "reality": "The Reality: It was codependency. I thought if I saved them, they would not leave me.",
            },
            {
                "title": "The Habit: Burnout from carrying other people's emotional baggage.",
                "body": 'The Lie: "People just rely on me."',
                "reality": "The Reality: I trained them to rely on me because being needed felt like being loved.",
            },
            {
                "title": "What actually helped",
                "body": "I had to retire from being the General Manager of the Universe. When I feel the urge to fix, I open Nafsy instead.",
                "reality": 'I write: "This is not my crisis to manage." It helps me put the responsibility back where it belongs.',
            },
        ],
    },
    {
        "id": 26,
        "title": "Why I felt like a fraud even when I succeeded",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": 'The Thought: "I just got lucky."',
                "body": 'The Lie: "I am humble."',
                "reality": "The Reality: I could not internalize my success. I did not believe I was good enough to earn it.",
            },
            {
                "title": 'The Thought: "They are going to find me out."',
                "body": 'The Lie: "I need to work harder to stay ahead."',
                "reality": "The Reality: I was living in fear of being exposed, so I over-prepared for everything.",
            },
            {
                "title": "The Thought: Focusing on the one mistake in a perfect project.",
                "body": 'The Lie: "I have high standards."',
                "reality": "The Reality: Perfectionism was my defense. If I am perfect, no one can hurt me.",
            },
            {
                "title": 'The Thought: "Everyone else knows what they are doing."',
                "body": 'The Lie: "I am the only one faking it."',
                "reality": "The Reality: Everyone is figuring it out. I was comparing my messy insides to their curated outsides.",
            },
            {
                "title": "What actually helped",
                "body": "I started keeping a Win List. I use Nafsy to log small wins daily, even just 'I sent the email.'",
                "reality": "It forces my brain to see the evidence that I am actually capable.",
            },
        ],
    },
    {
        "id": 27,
        "title": "Why I sabotaged moments of joy",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Feeling: Waiting for the other shoe to drop.",
                "body": 'The Lie: "I am just being realistic."',
                "reality": "The Reality: My nervous system associated calm with the calm before the storm.",
            },
            {
                "title": "The Behavior: Picking a fight when things were going too well.",
                "body": 'The Lie: "We have issues to resolve."',
                "reality": "The Reality: Chaos felt familiar. Happiness felt suspicious.",
            },
            {
                "title": "The Behavior: Numbing out during special moments.",
                "body": 'The Lie: "I am just tired."',
                "reality": "The Reality: I was dissociating because the joy felt too vulnerable.",
            },
            {
                "title": "The Behavior: Do not get your hopes up.",
                "body": 'The Lie: "I am managing expectations."',
                "reality": "The Reality: I was pre-grieving. I thought if I did not get happy, I would not get hurt.",
            },
            {
                "title": "What actually helped",
                "body": "I had to build tolerance for joy. I use Nafsy to note glimmers, tiny good things that happened.",
                "reality": "It teaches my brain that it is safe to feel good, even for just a minute.",
            },
        ],
    },
    {
        "id": 28,
        "title": "Why I stared at the wall instead of cleaning",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Behavior: Sitting on the edge of the bed for 20 minutes with one sock on.",
                "body": 'The Lie: "I am so lazy."',
                "reality": "The Reality: My brain's starter motor was broken. I knew what to do, but could not initiate the action.",
            },
            {
                "title": "The Behavior: Letting dishes pile up until I had no spoons left.",
                "body": 'The Lie: "I am a slob."',
                "reality": "The Reality: The task felt like 100 steps, not one. I was overwhelmed by the sequence.",
            },
            {
                "title": "The Behavior: waiting until the last minute to start work.",
                "body": 'The Lie: "I work better under pressure."',
                "reality": "The Reality: I needed the adrenaline of panic to override the paralysis.",
            },
            {
                "title": "The Behavior: Forgetting to eat or pee while hyper-focused.",
                "body": 'The Lie: "I am just in the zone."',
                "reality": "The Reality: Poor interoception. My brain was not receiving the body's signals.",
            },
            {
                "title": "What actually helped",
                "body": "Shaming myself into action never worked. Now, I break the task down in Nafsy. Instead of 'Clean house,' I write 'Pick up one cup.'",
                "reality": "Low friction is the only way I get moving.",
            },
        ],
    },
    {
        "id": 29,
        "title": "Why I disappeared for 3 days after a party",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Symptom: Physical exhaustion after socializing.",
                "body": 'The Lie: "I am depressed."',
                "reality": "The Reality: I spent the whole night masking, performing a version of myself to fit in.",
            },
            {
                "title": "The Symptom: Replaying every conversation (The Post-Mortem).",
                "body": 'The Lie: "I am just reflecting."',
                "reality": "The Reality: My anxiety was scanning the night for mistakes I might have made.",
            },
            {
                "title": "The Symptom: Irritability with my partner or family the next day.",
                "body": 'The Lie: "They are annoying me."',
                "reality": "The Reality: My social battery was in the negatives. I needed silence to recharge.",
            },
            {
                "title": "The Symptom: Dread about the next event.",
                "body": 'The Lie: "I hate people."',
                "reality": "The Reality: I do not hate people; I hate how drained I feel afterwards.",
            },
            {
                "title": "What actually helped",
                "body": "I stopped booking back-to-back plans. I use Nafsy to schedule recovery time just like I schedule the event.",
                "reality": "If I do not respect my battery, my body shuts me down.",
            },
        ],
    },
    {
        "id": 30,
        "title": "Why saying no made me feel sick",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Feeling: A knot in my stomach after setting a limit.",
                "body": 'The Lie: "I was too mean."',
                "reality": "The Reality: I was breaking a conditioned role. I was trained to be easy, so no felt dangerous.",
            },
            {
                "title": "The Behavior: Over-explaining why I could not come.",
                "body": 'The Lie: "They need to understand."',
                "reality": "The Reality: I was asking for permission to have needs.",
            },
            {
                "title": "The Behavior: Changing my mind and saying yes later.",
                "body": 'The Lie: "I can make it work."',
                "reality": "The Reality: The guilt was heavier than the exhaustion, so I caved to relieve the guilt.",
            },
            {
                "title": "The Behavior: Assuming they were mad because I did not reply instantly.",
                "body": 'The Lie: "I am a bad friend."',
                "reality": "The Reality: Reasonable people respect boundaries. I was projecting my own fears onto them.",
            },
            {
                "title": "What actually helped",
                "body": "I learned that guilt is just a side effect of growth. I track the feeling in Nafsy: I feel guilty, but I stayed safe.",
                "reality": "It reminds me that the discomfort means the boundary is working.",
            },
        ],
    },
    {
        "id": 31,
        "title": "Why spending money made me feel unsafe",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Habit: Hoarding money but never enjoying it.",
                "body": 'The Lie: "I am just frugal."',
                "reality": "The Reality: I was trying to build a wall of cash to protect me from the unpredictability of life.",
            },
            {
                "title": "The Habit: Panic buying when things were on sale.",
                "body": 'The Lie: "It is a good deal."',
                "reality": "The Reality: Scarcity mindset. If I do not get it now, it will be gone forever.",
            },
            {
                "title": "The Habit: Guilt after buying necessities (like groceries).",
                "body": 'The Lie: "I should not have bought the good brand."',
                "reality": "The Reality: I did not believe I deserved to be taken care of.",
            },
            {
                "title": "The Habit: Constantly checking my bank account.",
                "body": 'The Lie: "I am responsible."',
                "reality": "The Reality: It was a compulsion. I was checking to make sure the safety net was still there.",
            },
            {
                "title": "What actually helped",
                "body": "I had to separate my self-worth from my net worth. When the panic hits, I log it in Nafsy.",
                "reality": "I am safe. I have enough for today. It calms the survival brain.",
            },
        ],
    },
    {
        "id": 32,
        "title": "Why I could not cry even when I was sad",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Symptom: Feeling blank during tragedies or good news.",
                "body": 'The Lie: "I am heartless."',
                "reality": "The Reality: My emotional circuit breaker tripped. The feelings were too big, so the system shut down.",
            },
            {
                "title": "The Symptom: Losing hours of time scrolling or staring.",
                "body": 'The Lie: "I am bored."',
                "reality": "The Reality: I was checking out of reality because being present was too painful.",
            },
            {
                "title": "The Symptom: Feeling like I was watching myself in a movie.",
                "body": 'The Lie: "I am weird."',
                "reality": "The Reality: Depersonalization. It is a common anxiety symptom where you detach from your body.",
            },
            {
                "title": "The Symptom: Eating or drinking to feel something.",
                "body": 'The Lie: "I am hungry."',
                "reality": "The Reality: I was trying to manually stimulate my nervous system to wake it up.",
            },
            {
                "title": "What actually helped",
                "body": "You cannot force feelings back online. You have to invite them. I use Nafsy to just name the numbness: I feel empty right now.",
                "reality": "Acknowledging the void is usually the first step to filling it.",
            },
        ],
    },
    {
        "id": 33,
        "title": "Why I was obsessed with being good",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Habit: Never breaking a rule, ever.",
                "body": 'The Lie: "I have high morals."',
                "reality": "The Reality: I was terrified of authority. I thought one mistake would ruin my life.",
            },
            {
                "title": "The Habit: Swallowing my anger.",
                "body": 'The Lie: "I am just a calm person."',
                "reality": "The Reality: I learned that good kids do not get angry. So I hid my authentic self to be good.",
            },
            {
                "title": "The Habit: Working until I dropped.",
                "body": 'The Lie: "Hard work pays off."',
                "reality": "The Reality: I was trying to earn love through achievement.",
            },
            {
                "title": "The Habit: Panic when I thought someone was disappointed.",
                "body": 'The Lie: "I respect their opinion."',
                "reality": "The Reality: Disappointment felt like rejection. I needed approval to feel valid.",
            },
            {
                "title": "What actually helped",
                "body": "I had to learn that I am worthy even when I am bad or messy. I vent the bad thoughts into Nafsy.",
                "reality": "It is the one place I do not have to be the perfect child. I can just be human.",
            },
        ],
    },
    {
        "id": 34,
        "title": "Why I refused to go to sleep at a normal time",
        "subtitle": "(My therapist told me)",
        "slides": [
            {
                "title": "The Habit: Staying up until 2 AM doing nothing important.",
                "body": 'The Lie: "I am a night owl."',
                "reality": "The Reality: Revenge Bedtime Procrastination. I had no control over my day, so I stole time back at night.",
            },
            {
                "title": "The Habit: The dread of tomorrow.",
                "body": 'The Lie: "I am not tired."',
                "reality": "The Reality: Going to sleep meant tomorrow would come faster. Staying awake felt like pausing time.",
            },
            {
                "title": "The Habit: Racing thoughts the second the lights went out.",
                "body": 'The Lie: "My brain is just active."',
                "reality": "The Reality: The silence was too loud. I needed the distraction of my phone to drown out the worries.",
            },
            {
                "title": "The Habit: Waking up exhausted and regretting it.",
                "body": 'The Lie: "I will go to bed early tonight."',
                "reality": "The Reality: The cycle repeated because I never fixed the root cause: a lack of freedom during the day.",
            },
            {
                "title": "What actually helped",
                "body": "I stopped fighting the clock and started reclaiming my day. I do a brain dump in Nafsy before I brush my teeth.",
                "reality": "Putting the day away mentally helps me finally close my eyes.",
            },
        ],
    },
]


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:50]


def prefix_dash(text: str) -> str:
    text = (text or "").strip()
    if not text.startswith("-"):
        return f"- {text}"
    return text


def normalize_title(title: str) -> str:
    return number_re.sub("", title or "").strip()


def list_images(folder: str) -> List[str]:
    return [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if not name.startswith(".") and name.lower().endswith(VALID_EXTS)
    ]


def pick_random(folder: str) -> str:
    images = list_images(folder)
    if not images:
        raise RuntimeError(f"No images found in {folder}")
    return random.choice(images)


def pick_many_unique(folder: str, n: int) -> List[str]:
    images = list_images(folder)
    if not images:
        raise RuntimeError(f"No images found in {folder}")
    if n <= len(images):
        return random.sample(images, n)

    picked = images.copy()
    while len(picked) < n:
        picked.append(random.choice(images))
    random.shuffle(picked)
    return picked[:n]


def make_cover(deck_title: str, deck_subtitle: str) -> Dict[str, object]:
    return {"type": "cover", "texts": {"title": deck_title, "subtitle": deck_subtitle}}


def make_content(title: str, body: str, reality: str = None) -> Dict[str, object]:
    return {
        "type": "content",
        "texts": {
            "title": prefix_dash(normalize_title(title)),
            "body": body.strip() if body else "",
            "reality": reality.strip() if reality else reality,
        },
    }


def slide6_text_blob(slide: Dict[str, object]) -> str:
    texts = slide.get("texts", {})
    return " ".join(
        [
            str(texts.get("title", "")),
            str(texts.get("body", "")),
            str(texts.get("reality", "") or ""),
        ]
    ).lower()


def choose_demo_dir_from_slide6(text: str) -> str:
    exercise_signals = ["exercise", "breath", "breathing", "ground", "grounding", "mindfulness"]
    chat_signals = ["chat", "vent", "rant", "talk it out", "brain dump"]
    mood_signals = ["mood", "log", "track", "check in", "check-in", "battery", "glimmer", "fact check"]

    if any(signal in text for signal in exercise_signals):
        return DEMO_EXERCISE_DIR
    if any(signal in text for signal in chat_signals):
        return DEMO_CHAT_DIR
    if any(signal in text for signal in mood_signals):
        return random.choice([DEMO_MOOD_DIR, DEMO_YEAR_DIR])
    return random.choice(DEMO_DIRS)


def ensure_required_folders() -> None:
    required = [HOOKS_DIR, SLIDES_DIR, DEMO_MOOD_DIR, DEMO_YEAR_DIR, DEMO_CHAT_DIR, DEMO_EXERCISE_DIR]
    for folder in required:
        if not os.path.isdir(folder):
            raise RuntimeError(f"Missing folder: {folder}")
        if not list_images(folder):
            raise RuntimeError(f"No images found in: {folder}")

    if len(DECKS) != 14:
        raise RuntimeError(f"Expected 14 decks, got {len(DECKS)}")

    os.makedirs(OUTPUT_ROOT, exist_ok=True)


def assign_images(contents: List[Dict[str, object]]) -> List[str]:
    if len(contents) != 6:
        raise RuntimeError(f"Each deck must contain exactly 6 slides (got {len(contents)})")

    hook_image = pick_random(HOOKS_DIR)
    middle_images = pick_many_unique(SLIDES_DIR, 4)
    slide6_folder = choose_demo_dir_from_slide6(slide6_text_blob(contents[5]))
    slide6_image = pick_random(slide6_folder)
    return [hook_image] + middle_images + [slide6_image]


def save_slideshow(deck_id: int, title: str, subtitle: str, slides: List[Dict[str, str]]) -> None:
    out_dir = os.path.join(OUTPUT_ROOT, f"show_{deck_id:02d}_{slugify(title)}")
    os.makedirs(out_dir, exist_ok=True)

    content_slides = [make_content(s["title"], s["body"], s["reality"]) for s in slides]
    contents = [make_cover(title, subtitle)] + content_slides
    images = assign_images(contents)

    for index, (img_path, slide) in enumerate(zip(images, contents), 1):
        output_path = os.path.join(out_dir, f"slide_{index:02d}.jpg")
        process_slide(
            img_path,
            output_path,
            slide["type"],
            slide["texts"],
            aspect_ratio=ASPECT_RATIO,
            sizes=SIZES,
        )


def main() -> None:
    random.seed()
    ensure_required_folders()

    for deck in DECKS:
        if len(deck["slides"]) != 5:
            raise RuntimeError(f"Deck {deck['id']} must include 5 content slides")
        save_slideshow(deck["id"], deck["title"], deck["subtitle"], deck["slides"])

    print(f"Generated {len(DECKS)} slideshows into {OUTPUT_ROOT}/")


if __name__ == "__main__":
    main()
