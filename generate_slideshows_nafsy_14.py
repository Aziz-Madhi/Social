#!/usr/bin/env python3
import os
import random
import re
from copy import deepcopy
from typing import Dict, List, Optional, Tuple

from slideshow_tool import process_slide

BASE_DIR = "/Users/azizmadhi/Apps/Social"
CONTENT_DIR = os.path.join(BASE_DIR, "raw_images", "newforamt photos")
HOOKS_DIR = CONTENT_DIR
DEMO_CHAT_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "chat")
DEMO_MOOD_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "mood")
DEMO_YEAR_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "year view")
DEMO_EXERCISE_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "exercise")
OUTPUT_ROOT = os.path.join(BASE_DIR, "ready_to_post")
ASPECT_RATIO = "3:4"

VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp")

STYLE_SIZES = {
    # Tuned to the new references.
    "cover_title": 49,
    "cover_subtitle": 33,
    "content": 43,
    "cover_title_max_width_ratio": 0.84,
    "cover_subtitle_max_width_ratio": 0.82,
    "content_max_width_ratio": 0.83,
    # Larger vertical spacing between blocks.
    "title_body_gap": 1.05,
    "body_reality_gap": 1.25,
    "cover_subtitle_gap": 0.35,
}

STYLE_STROKE = {
    "width": 3,
    "color": "black",
    "fill": "white",
}


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:60]


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def list_images(folder: str) -> List[str]:
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if not name.startswith(".") and name.lower().endswith(VALID_EXTS)
    ]


def require_non_empty_folder(folder: str, label: str) -> None:
    if not os.path.isdir(folder):
        raise RuntimeError(f"Missing required folder for {label}: {folder}")
    images = list_images(folder)
    if not images:
        raise RuntimeError(f"No images found in required folder for {label}: {folder}")


def build_pool(folder: str) -> List[str]:
    images = list_images(folder)
    random.shuffle(images)
    return images


def pop_or_random_unique(pool: List[str], folder: str, used_in_show: set[str]) -> str:
    while pool:
        candidate = pool.pop()
        if candidate not in used_in_show:
            return candidate

    images = [img for img in list_images(folder) if img not in used_in_show]
    if not images:
        raise RuntimeError(
            f"Not enough unique images in folder for this slideshow: {folder}"
        )
    return random.choice(images)


def has_app_mention(slide: Dict[str, str]) -> bool:
    text = " ".join(
        [
            slide.get("title", ""),
            slide.get("body", ""),
            slide.get("reality", "") or "",
        ]
    ).lower()
    return ("nafsy" in text) or ("nafsi" in text)


def choose_demo_bucket(slide: Dict[str, str]) -> Tuple[str, str]:
    text = " ".join(
        [
            slide.get("title", ""),
            slide.get("body", ""),
            slide.get("reality", "") or "",
        ]
    ).lower()

    exercise_signals = ["exercise", "breathe", "breathing", "mindfulness", "grounding", "4-7-8"]
    chat_signals = ["chat", "vent", "rant", "talk it out", "obsessive thoughts", "loop"]
    year_signals = ["year", "monthly", "over time", "pattern view", "view"]
    mood_signals = ["mood", "track", "log", "check-in", "check in", "emotion"]

    if any(signal in text for signal in exercise_signals):
        return ("demo/exercise", DEMO_EXERCISE_DIR)
    if any(signal in text for signal in chat_signals):
        return ("demo/chat", DEMO_CHAT_DIR)
    if any(signal in text for signal in year_signals):
        return ("demo/year view", DEMO_YEAR_DIR)
    if any(signal in text for signal in mood_signals):
        return ("demo/mood", DEMO_MOOD_DIR)
    return ("demo/mood", DEMO_MOOD_DIR)


def split_hook_text(hook: str) -> Tuple[str, Optional[str]]:
    hook = normalize_text(hook)
    m = re.match(r"^(.*?)(\([^)]*\))\s*$", hook)
    if m:
        title = m.group(1).strip()
        subtitle = m.group(2).strip()
        if title:
            return title, subtitle
    return hook, None


def make_cover(hook: str) -> Dict[str, object]:
    title, subtitle = split_hook_text(hook)
    return {"type": "cover", "texts": {"title": title, "subtitle": subtitle}}


def make_content(title: str, body: str) -> Dict[str, object]:
    return {
        "type": "content",
        "texts": {
            "title": normalize_text(title),
            "body": normalize_text(body),
            "reality": None,
        },
    }


def starts_with_number_marker(text: str) -> bool:
    return bool(re.match(r"^\s*\d+[\)\.\-:]\s*", text or ""))


def ensure_numbering_sequence(slides: List[Dict[str, object]]) -> None:
    # If slide 3 starts with "2)" (or similar) and slide 2 is unnumbered, force "1)" on slide 2.
    if len(slides) < 3:
        return
    second = slides[1]["texts"]["title"]
    third = slides[2]["texts"]["title"]
    if re.match(r"^\s*2[\)\.\-:]\s*", third or "") and not starts_with_number_marker(second):
        slides[1]["texts"]["title"] = f"1) {second}".strip()


def split_body_blocks(slides: List[Dict[str, object]]) -> None:
    # Keep a consistent "title + main + closing" style when content is long enough.
    for slide in slides[1:]:
        texts = slide.get("texts", {})
        if texts.get("reality") is not None:
            texts["reality"] = normalize_text(texts.get("reality"))
            continue

        body = normalize_text(texts.get("body", ""))
        sentences = re.split(r"(?<=[.!?])\s+", body)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 3:
            texts["body"] = body
            texts["reality"] = None
            continue

        # Use the last 1-2 short sentences as the closing block for visual separation.
        tail = [sentences[-1]]
        if len(sentences) >= 4:
            two_tail = [sentences[-2], sentences[-1]]
            if len(" ".join(two_tail)) <= 125:
                tail = two_tail

        head_count = len(sentences) - len(tail)
        texts["body"] = " ".join(sentences[:head_count]).strip()
        texts["reality"] = " ".join(tail).strip()


SLIDESHOWS: List[Tuple[str, List[Dict[str, object]]]] = [
    (
        "5 ways I stay (healthily) detached in a relationship (part 2)",
        [
            make_cover("5 ways I stay (healthily) detached in a relationship (part 2)"),
            make_content(
                "never cancel plans with friends for him",
                "your world existed before him. it must exist during him. canceling plans signals to your brain that he is the only source of dopamine.",
            ),
            make_content(
                "2) stop trying to read his mind",
                "anxiety loves to fill in the blanks. if he hasn't said it, it isn't real. assume the best or ask directly. mind reading is a form of self-sabotage.",
            ),
            make_content(
                "3) regulate your own nervous system first",
                "before i react to a dry text, i check in with myself. i use nafsy to log the emotion and get the panic out of my system. usually, i realize i'm not mad at him, i'm just overstimulated. react to reality, not your triggers.",
            ),
            make_content(
                "4) have a hobby he can't touch",
                "something that is just yours. painting, running, reading. it reminds you that you are a whole person without his validation.",
            ),
            make_content(
                "5) romanticize your solitude",
                "enjoy your own company so much that his presence is a nice addition, not a necessity. you are the main character. he is the love interest. don't confuse the roles.",
            ),
        ],
    ),
    (
        "things i do to (actually) fill my cup (these changed my life overnight)",
        [
            make_cover("things i do to (actually) fill my cup (these changed my life overnight)"),
            make_content(
                "slow mornings are non-negotiable",
                "rushing creates cortisol before you even brush your teeth. i wake up 20 minutes early just to sit in silence. protect your peace before the world tries to steal it.",
            ),
            make_content(
                "2) consume content that feels like a hug",
                "unfollow anyone who makes you feel like you aren't enough. your eyes are feeding your brain. stop feeding it junk food.",
            ),
            make_content(
                "3) treating my feelings like data",
                "ignoring sadness makes it louder. i track my daily mood swings on nafsy just to see the patterns. realizing my \"bad days\" usually happen when i haven't slept helps me stop spiraling. awareness is the antidote to anxiety.",
            ),
            make_content(
                "4) date yourself once a week",
                "take yourself to coffee. buy the flowers. teach your subconscious how you expect to be treated. you set the standard.",
            ),
        ],
    ),
    (
        "5 unhinged ways I stayed detached during no contact",
        [
            make_cover("5 unhinged ways I stayed detached during no contact"),
            make_content(
                "talk to him in your notes app",
                "never send the text. write it out, read it, delete it. the urge to text is just energy seeking release. let it out without letting him back in.",
            ),
            make_content(
                "2) become obsessed with your own glow up",
                "redirect that obsessive energy from \"what is he doing?\" to \"how can i level up?\" vanity is better than misery. make him regret losing you by becoming the best version of you.",
            ),
            make_content(
                "3) externalize the delusion",
                "i stopped venting to friends who were tired of hearing it. i started using nafsy to chat through the obsessive thoughts. getting the loop out of my head and onto a screen breaks the cycle. it's cheaper than therapy and saves my friendships.",
            ),
            make_content(
                "4) the \"ick\" list",
                "make a list of everything he did that annoyed you. read it every time you miss him. your brain is romanticizing the memory, not the man. force it to remember the reality.",
            ),
        ],
    ),
    (
        "5 signs your body is BEGGING you to leave him (im on your fyp for a reason)",
        [
            make_cover("5 signs your body is BEGGING you to leave him (im on your fyp for a reason)"),
            make_content(
                "you feel exhausted after hanging out",
                "not \"good\" tired. drained tired. your body burns energy trying to feel safe around unsafe people. fatigue is a major red flag.",
            ),
            make_content(
                "2) your stomach acts up when you see his name",
                "the gut-brain connection is real. nausea isn't butterflies. it's your intuition screaming \"danger.\"",
            ),
            make_content(
                "3) you analyze every conversation later",
                "healthy love is simple. if you have to dissect his words to find reassurance, you are starving. i use nafsy to log how i feel immediately after he leaves. seeing \"anxious\" logged 5 days in a row made me realize the truth my heart ignored.",
            ),
            make_content(
                "4) you are sick all the time",
                "constant colds, headaches, body aches. your immune system is suppressed by chronic stress. your body will shut down if you don't walk away.",
            ),
        ],
    ),
    (
        "5 subtle signs a man is actually in love with you (not just attracted)",
        [
            make_cover("5 subtle signs a man is actually in love with you (not just attracted)"),
            make_content(
                "he regulates you, he doesn't rattle you",
                "lust feels like a rollercoaster. love feels like a calm ocean. if your nervous system settles when he walks in, that's the sign.",
            ),
            make_content(
                "2) he remembers the small things",
                "you mentioned a flower once. he brings it. active listening is the highest form of respect. it means he holds space for you in his mind.",
            ),
            make_content(
                "3) consistency over intensity",
                "love-bombing is intense but fleeting. real love is boringly consistent. logging my \"calm\" moments on nafsy helped me realize that safety feels different than the \"spark\" i was used to. boring is good. boring is safe.",
            ),
            make_content(
                "4) he includes you in the future",
                "not \"someday.\" concrete plans. a man who loves you wants to secure his spot in your life.",
            ),
        ],
    ),
    (
        "5 lies avoidants tell to end relationships (and what they really mean)",
        [
            make_cover("5 lies avoidants tell to end relationships (and what they really mean)"),
            make_content(
                "\"i need to work on myself\"",
                "translation: i am terrified of intimacy and i am choosing to run rather than communicate. they are protecting their independence, not their growth.",
            ),
            make_content(
                "2) \"you deserve better\"",
                "translation: i am not willing to give you what you need. believe them. this is a confession, not a compliment.",
            ),
            make_content(
                "3) \"i just lost feelings\"",
                "feelings don't vanish, they get deactivated. deactivation is a defense mechanism. i use the mindfulness prompts on nafsy to remind myself that their emotional shutdown is not a reflection of my worth. do not internalize their inability to connect.",
            ),
            make_content(
                "4) \"i'm not ready for a relationship right now\"",
                "translation: i want the benefits of you without the responsibility of you. timing is rarely the issue. fear is.",
            ),
        ],
    ),
    (
        "5 signs your body is BEGGING you to slow down (but you keep ignoring them)",
        [
            make_cover("5 signs your body is BEGGING you to slow down (but you keep ignoring them)"),
            make_content(
                "you clinch your jaw without noticing",
                "tension stores where we hold back words. release your tongue from the roof of your mouth. drop your shoulders. exhale.",
            ),
            make_content(
                "2) you can't watch a movie without your phone",
                "the inability to do one thing at a time is a symptom of a fried dopamine receptor. boredom feels dangerous to a chaotic mind. practice doing nothing.",
            ),
            make_content(
                "3) everything irritates you",
                "when your cup is full, even a drop of water causes a spill. irritability is your body's way of asking for space. instead of snapping, i take 5 minutes to vent on nafsy. getting the anger out privately protects my peace publicly.",
            ),
            make_content(
                "4) you forget simple words",
                "brain fog is the brain's emergency brake. it means \"system overloaded.\" stop pushing. start resting.",
            ),
        ],
    ),
    (
        "5 more unhinged ways i stay (healthily) detached in a relationship",
        [
            make_cover("5 more unhinged ways i stay (healthily) detached in a relationship"),
            make_content(
                "assume he loves you, then ignore him",
                "operate from confidence, not lack. when you know you are the prize, you don't need to check if he's still holding the trophy. go live your life.",
            ),
            make_content(
                "2) match energy minus 10%",
                "if he pulls back, you pull back further. never chase. chasing puts you in the masculine energy of \"pursuit.\" stay in your feminine energy of \"receiving.\"",
            ),
            make_content(
                "3) the 24-hour rule for big feelings",
                "never bring up a \"heavy\" topic while triggered. write it down first. i dump the entire emotional rant into nafsy and wait 24 hours. 90% of the time, the feeling passes and i save myself an unnecessary fight.",
            ),
            make_content(
                "4) keep your mystery",
                "don't tell him every thought in your head. intimacy requires distance. leave him wondering what you're thinking.",
            ),
        ],
    ),
    (
        "things i do to (actually) fill my cup (part 2)",
        [
            make_cover("things i do to (actually) fill my cup (part 2)"),
            make_content(
                "protect the first hour of the day",
                "no scrolling. no emails. the world can wait 60 minutes. your brain needs time to boot up before it starts processing other people's lives.",
            ),
            make_content(
                "2) high-vibe playlists only",
                "music reprograms your subconscious. stop listening to sad songs and wondering why you feel sad. listen to frequencies that lift you.",
            ),
            make_content(
                "3) intentional venting",
                "complaining rewires your brain for negativity. processing releases it. there is a difference. i use the mood logger on nafsy to identify the feeling, feel it, and then let it go. don't live in the vent. visit it, then leave.",
            ),
            make_content(
                "4) nature walks without headphones",
                "let the birds be the podcast. let the wind be the music. grounding yourself in reality is the quickest way to lower cortisol.",
            ),
        ],
    ),
    (
        "5 lies avoidants tell to end relationships (part 2)",
        [
            make_cover("5 lies avoidants tell to end relationships (part 2)"),
            make_content(
                "\"i'm too busy for a relationship\"",
                "people make time for what they want. barack obama had a wife while running a country. he isn't busy. you just aren't a priority.",
            ),
            make_content(
                "2) \"we moved too fast\"",
                "they set the pace. avoidants love-bomb to secure the bond, then panic when it gets real. you didn't move too fast. they ran until they got scared.",
            ),
            make_content(
                "3) \"it's not you, it's me\"",
                "actually, this one is true. it is them. it is their unhealed trauma. using nafsy to track my own emotional stability reminds me that i am not the problem. let them keep their problems.",
            ),
            make_content(
                "4) \"i don't want to hurt you\"",
                "then why are you doing the exact thing that hurts me? this is manipulation disguised as empathy. closure is realizing they are confused and you don't have to be.",
            ),
        ],
    ),
    (
        "5 subtle signs a man is actually in love with you (part 2)",
        [
            make_cover("5 subtle signs a man is actually in love with you (part 2)"),
            make_content(
                "he protects your peace",
                "he doesn't bring drama. he handles the problem before it reaches you. he wants your life to be easier because he is in it.",
            ),
            make_content(
                "2) he asks for your opinion",
                "he values your mind, not just your body. when a man respects your logic, he sees you as a partner.",
            ),
            make_content(
                "3) vulnerability without prompting",
                "he tells you his fears. men are conditioned to be stoic. if he shows you his soft side, you are his safe space. i log these moments of connection in nafsy so i remember them when my anxiety tries to convince me otherwise.",
            ),
            make_content(
                "4) he adopts your mannerisms",
                "mirroring is a subconscious sign of deep bonding. if he starts using your slang, he's tuning into your frequency.",
            ),
        ],
    ),
    (
        "5 signs your body is BEGGING you to leave him (part 2)",
        [
            make_cover("5 signs your body is BEGGING you to leave him (part 2)"),
            make_content(
                "you feel lonely when you are with him",
                "the worst loneliness isn't being alone. it's being with someone who makes you feel unseen. emotional neglect triggers the same pain centers as physical injury.",
            ),
            make_content(
                "2) your sleep is garbage",
                "waking up at 3am with a racing heart? your cortisol is spiking because your body is on high alert. you are sleeping next to the source of your stress.",
            ),
            make_content(
                "3) you have stopped doing things you love",
                "you stopped painting. you stopped seeing friends. you shrank yourself to fit into his box. i noticed on nafsy that my \"joy\" entries stopped the month i started dating him. data doesn't lie.",
            ),
            make_content(
                "4) you feel relief when plans get cancelled",
                "that isn't introversion. that is freedom. listen to the relief.",
            ),
        ],
    ),
    (
        "5 ways I stay (healthily) detached in a relationship (part 3)",
        [
            make_cover("5 ways I stay (healthily) detached in a relationship (part 3)"),
            make_content(
                "keep your finances separate",
                "financial dependence creates emotional dependence. having your own \"exit fund\" allows you to stay because you want to, not because you have to. freedom is sexy.",
            ),
            make_content(
                "2) don't make him your therapist",
                "he is your boyfriend, not your emotional rehabilitation center. dumping all your trauma on him creates an imbalance. use tools like nafsy to process the heavy stuff, then bring the healed version of you to the relationship.",
            ),
            make_content(
                "3) maintain mystery",
                "you don't need to answer every text in 30 seconds. you don't need to report your every move. autonomy creates attraction.",
            ),
            make_content(
                "4) prioritize your sleep over his schedule",
                "don't stay up late just because he is up. don't skip the gym because he wants to cuddle. resentment builds when you sacrifice your routine.",
            ),
        ],
    ),
    (
        "5 signs your body is BEGGING you to slow down (part 2)",
        [
            make_cover("5 signs your body is BEGGING you to slow down (part 2)"),
            make_content(
                "eye twitching",
                "magnesium deficiency and stress. your nerves are literally firing without your permission. close your eyes. breathe.",
            ),
            make_content(
                "2) zero libido",
                "survival mode kills desire. your body thinks it is running from a bear. it doesn't have time to reproduce. safety is the strongest aphrodisiac.",
            ),
            make_content(
                "3) crying over spilled milk",
                "literally. when small inconveniences make you weep, your emotional bucket is overflowing. empty the bucket. i use the vent feature on nafsy to cry it out digitally so i don't breakdown in the kitchen. release is necessary.",
            ),
            make_content(
                "4) shallow breathing",
                "you are breathing into your chest, not your belly. this keeps you in fight or flight. put a hand on your stomach. inhale for 4. hold for 7. exhale for 8.",
            ),
        ],
    ),
]


def build_pools() -> Dict[str, List[str]]:
    return {
        "hooks": build_pool(HOOKS_DIR),
        "content": build_pool(CONTENT_DIR),
        "demo/chat": build_pool(DEMO_CHAT_DIR),
        "demo/mood": build_pool(DEMO_MOOD_DIR),
        "demo/year view": build_pool(DEMO_YEAR_DIR),
        "demo/exercise": build_pool(DEMO_EXERCISE_DIR),
    }


def choose_image_for_slide(
    slide_index: int,
    slide: Dict[str, object],
    pools: Dict[str, List[str]],
    used_in_show: set[str],
) -> Tuple[str, str]:
    if slide_index == 1:
        return ("hook", pop_or_random_unique(pools["hooks"], HOOKS_DIR, used_in_show))

    texts = slide.get("texts", {})
    if has_app_mention(texts):
        bucket, folder = choose_demo_bucket(texts)
        return (bucket, pop_or_random_unique(pools[bucket], folder, used_in_show))

    return (
        "content",
        pop_or_random_unique(pools["content"], CONTENT_DIR, used_in_show),
    )


def save_slideshow(index: int, title: str, slides: List[Dict[str, object]], pools: Dict[str, List[str]]) -> None:
    folder_name = f"show_{index:02d}_{slugify(title)}"
    out_dir = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(out_dir, exist_ok=True)
    used_in_show: set[str] = set()

    for slide_idx, slide in enumerate(slides, 1):
        bucket, image_path = choose_image_for_slide(slide_idx, slide, pools, used_in_show)
        used_in_show.add(image_path)
        output_path = os.path.join(out_dir, f"slide_{slide_idx:02d}.jpg")

        print(
            f"[show {index:02d} slide {slide_idx:02d}] bucket={bucket} "
            f"image={image_path} -> {output_path}"
        )

        process_slide(
            image_path,
            output_path,
            slide["type"],
            slide["texts"],
            aspect_ratio=ASPECT_RATIO,
            sizes=STYLE_SIZES,
            stroke_config=STYLE_STROKE,
            text_position="center",
        )


def verify_required_inputs() -> None:
    require_non_empty_folder(HOOKS_DIR, "hook images")
    require_non_empty_folder(CONTENT_DIR, "content images")
    require_non_empty_folder(DEMO_CHAT_DIR, "demo chat images")
    require_non_empty_folder(DEMO_MOOD_DIR, "demo mood images")
    require_non_empty_folder(DEMO_YEAR_DIR, "demo year view images")
    require_non_empty_folder(DEMO_EXERCISE_DIR, "demo exercise images")

    if len(SLIDESHOWS) != 14:
        raise RuntimeError(f"Expected 14 slideshows, got {len(SLIDESHOWS)}")


def main() -> None:
    verify_required_inputs()
    os.makedirs(OUTPUT_ROOT, exist_ok=True)
    pools = build_pools()

    for idx, (title, raw_slides) in enumerate(SLIDESHOWS, 1):
        slides = deepcopy(raw_slides)
        ensure_numbering_sequence(slides)
        split_body_blocks(slides)
        save_slideshow(idx, title, slides, pools)

    print(f"\nGenerated {len(SLIDESHOWS)} slideshows in {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
