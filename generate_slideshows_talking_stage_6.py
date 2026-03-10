#!/usr/bin/env python3
import argparse
import random
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Optional, Set, Tuple

from PIL import Image

from slideshow_tool import process_slide

BASE_DIR = Path("/Users/azizmadhi/Apps/Social")
IMAGE_DIR = BASE_DIR / "raw_images" / "newforamt photos"
OUTPUT_ROOT = BASE_DIR / "ready_to_post"
ASPECT_RATIO = "3:4"

VALID_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
EXCLUDED_BASENAMES = {"26fea4b7b81ca61b1ebd22c51c4d6bad.jpg"}

HOOK_STYLE_SIZES = {
    "cover_title": 60,
    "cover_subtitle": 31,
    "content": 54,
    "cover_title_max_width_ratio": 0.82,
    "cover_subtitle_max_width_ratio": 0.80,
    "content_max_width_ratio": 0.70,
    "title_body_gap": 1.05,
    "body_reality_gap": 1.05,
    "cover_subtitle_gap": 0.70,
    "cover_title_align": "center",
    "cover_subtitle_align": "left",
    "cover_subtitle_left_ratio": 0.10,
}

CONTENT_STYLE_SIZES = {
    "cover_title": 60,
    "cover_subtitle": 31,
    "content": 54,
    "cover_title_max_width_ratio": 0.82,
    "cover_subtitle_max_width_ratio": 0.80,
    "content_max_width_ratio": 0.70,
    "title_body_gap": 1.05,
    "body_reality_gap": 1.05,
    "cover_subtitle_gap": 0.70,
}

STYLE_STROKE = {
    "width": 2,
    "color": "black",
    "fill": "white",
}


@dataclass(frozen=True)
class SlideSpec:
    slide_type: str
    title: str
    body: Optional[str] = None
    reality: Optional[str] = None
    subtitle: Optional[str] = None


@dataclass(frozen=True)
class ImageMeta:
    path: Path


def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def normalize_symbol_line(text: Optional[str]) -> str:
    clean = normalize_text(text)
    return re.sub(r"^\s*([✨\*\-])\s*", "", clean, count=1)


def slugify(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", text.lower())
    return text.strip("_")[:60]


def list_images(folder: Path) -> List[Path]:
    if not folder.exists():
        return []
    return sorted(
        [
            p
            for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in VALID_EXTS and p.name not in EXCLUDED_BASENAMES
        ]
    )


def is_valid_image(path: Path) -> bool:
    try:
        if path.stat().st_size == 0:
            return False
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception:
        return False


def build_image_meta(paths: Iterable[Path]) -> List[ImageMeta]:
    metas: List[ImageMeta] = []
    for path in paths:
        if not is_valid_image(path):
            print(f"[skip] invalid image: {path}")
            continue
        metas.append(ImageMeta(path=path))
    return metas


def make_cover(title: str, subtitle: str) -> SlideSpec:
    return SlideSpec(slide_type="cover", title=normalize_text(title), subtitle=normalize_text(subtitle))


def make_content(title: str, body: str, closing: str) -> SlideSpec:
    return SlideSpec(
        slide_type="content",
        title=normalize_text(title),
        body=normalize_text(body),
        reality=normalize_symbol_line(closing),
    )


def starts_with_marker(text: str) -> bool:
    return bool(re.match(r"^\s*\d+[\)\.:-]\s*", text))


def ensure_numbering_sequence(slides: List[SlideSpec]) -> List[SlideSpec]:
    fixed: List[SlideSpec] = [slides[0]]
    expected = 1
    for slide in slides[1:]:
        title = slide.title
        if not starts_with_marker(title):
            title = f"{expected}) {title}"
        expected += 1
        fixed.append(
            SlideSpec(
                slide_type=slide.slide_type,
                title=title,
                body=slide.body,
                reality=slide.reality,
                subtitle=slide.subtitle,
            )
        )
    return fixed


def slide_text_payload(slide: SlideSpec) -> Dict[str, Optional[str]]:
    if slide.slide_type == "cover":
        return {"title": slide.title, "subtitle": slide.subtitle}
    return {"title": slide.title, "body": slide.body, "reality": slide.reality}


def ranked_random_candidates(
    rng: random.Random,
    images: List[ImageMeta],
    used_in_show: Set[Path],
    usage_count: DefaultDict[Path, int],
) -> List[ImageMeta]:
    candidates = [img for img in images if img.path not in used_in_show]
    if not candidates:
        raise RuntimeError("No unique image candidates left for this slideshow")

    grouped: Dict[int, List[ImageMeta]] = {}
    for img in candidates:
        grouped.setdefault(usage_count[img.path], []).append(img)

    ranked: List[ImageMeta] = []
    for use_count in sorted(grouped.keys()):
        bucket = grouped[use_count]
        rng.shuffle(bucket)
        ranked.extend(bucket)

    return ranked


def choose_image_for_slide(
    rng: random.Random,
    images: List[ImageMeta],
    used_in_show: Set[Path],
    usage_count: DefaultDict[Path, int],
) -> Tuple[ImageMeta, List[ImageMeta]]:
    ranked = ranked_random_candidates(rng, images, used_in_show, usage_count)
    top3 = ranked[:3]
    chosen = rng.choice(top3)
    return chosen, top3


def log_selection(
    show_idx: int,
    slide_idx: int,
    slide: SlideSpec,
    chosen: ImageMeta,
    top3: List[ImageMeta],
    usage_count: DefaultDict[Path, int],
) -> None:
    summary = slide.title.replace("\n", " ")
    if len(summary) > 80:
        summary = summary[:77] + "..."

    top3_str = ", ".join([f"{item.path.name}:used={usage_count[item.path]}" for item in top3])
    print(
        f"[show {show_idx:02d} slide {slide_idx:02d}] {summary} | "
        f"top3=[{top3_str}] | chosen={chosen.path.name}:used={usage_count[chosen.path]}"
    )


def save_slideshow(
    show_idx: int,
    title: str,
    slides: List[SlideSpec],
    rng: random.Random,
    images: List[ImageMeta],
    usage_count: DefaultDict[Path, int],
    dry_run: bool,
) -> None:
    folder_name = f"show_{show_idx:02d}_{slugify(title)}"
    out_dir = OUTPUT_ROOT / folder_name
    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)

    used_in_show: Set[Path] = set()

    for slide_idx, slide in enumerate(slides, start=1):
        chosen, top3 = choose_image_for_slide(
            rng=rng,
            images=images,
            used_in_show=used_in_show,
            usage_count=usage_count,
        )

        log_selection(show_idx, slide_idx, slide, chosen, top3, usage_count)

        used_in_show.add(chosen.path)
        usage_count[chosen.path] += 1

        if dry_run:
            continue

        output_path = out_dir / f"slide_{slide_idx:02d}.jpg"
        sizes = HOOK_STYLE_SIZES if slide.slide_type == "cover" else CONTENT_STYLE_SIZES
        text_position = "top" if slide.slide_type == "cover" else "center"

        process_slide(
            str(chosen.path),
            str(output_path),
            slide.slide_type,
            slide_text_payload(slide),
            aspect_ratio=ASPECT_RATIO,
            sizes=sizes,
            stroke_config=STYLE_STROKE,
            text_position=text_position,
        )


def validate_inputs(images: List[ImageMeta]) -> None:
    if not IMAGE_DIR.exists():
        raise RuntimeError(f"Missing source folder: {IMAGE_DIR}")

    # 6 slides per show, no repeats within show.
    if len(images) < 6:
        raise RuntimeError(
            "Not enough usable images. Need at least 6 unique files in "
            f"{IMAGE_DIR}, found {len(images)}"
        )


def build_slideshows() -> List[Tuple[str, List[SlideSpec]]]:
    return [
        (
            "Slideshow 1 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content('1. not explaining my "no."', "giving a reason gives them room to negotiate.", '"no" is a complete sentence. you don’t owe them a debate.'),
                    make_content("2) leaving when my body feels tight.", "staying out of politeness is self-betrayal.", "honor your exit strategy without guilt."),
                    make_content("3) tracking my triggers privately.", "venting to the wrong people spreads the chaos.", "my coach recommended the nafsy app to process my feelings safely before i react."),
                    make_content("4) letting people be wrong about me.", "correcting their narrative is exhausting.", "protect your peace, not your point."),
                    make_content("5) ignoring calls when i'm drained.", "access to your energy is a privilege.", "respond when you are regulated, not obligated."),
                ]
            ),
        ),
        (
            "Slideshow 2 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. matching their response time.", "instant replies train them to think you're always waiting.", "be busy living your life, not just looking at your screen."),
                    make_content("2) processing my anxiety alone.", "asking for reassurance too early kills the attraction.", "my therapist told me to use the nafsy app to journal the spiraling thoughts so i don't text them."),
                    make_content("3) keeping my weekends booked.", "don't clear your schedule for a \"maybe\" plan.", "if they wanted to see you, they would have booked you by wednesday."),
                    make_content("4) judging their actions, ignoring their words.", "\"i miss you\" means nothing if they haven't seen you in weeks.", "believe the behavior. it's the only truth."),
                    make_content("5) holding back wifey privileges.", "don't give relationship benefits at a talking stage price.", "let them earn the right to your vulnerability."),
                ]
            ),
        ),
        (
            "Slideshow 3 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. blocking access when i'm overwhelmed.", "you are not a 24/7 hotline for everyone's crisis.", "put the phone on dnd. the world can wait."),
                    make_content("2) refusing to fix their bad mood.", "you are not responsible for their emotional regulation.", "let them sit in their own discomfort. it's how they grow."),
                    make_content("3) checking in with myself first.", "i used to burn out trying to please everyone.", "now i use the nafsy app (my coach's tip) to check my energy battery before i say yes to plans."),
                    make_content("4) ending the conversation when voices raise.", "i don't negotiate with disrespect.", "walk away. teach them how to treat you."),
                    make_content("5) keeping my wins to myself.", "not everyone is happy for you, and that energy is heavy.", "share your joy only with those who can hold it."),
                ]
            ),
        ),
        (
            "Slideshow 4 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. not auditioning for the role.", "stop trying to prove you're \"good enough\" for them.", "assess if they are good enough for you. flip the script."),
                    make_content("2) stopping the \"cool girl\" act.", "pretending you don't have needs backfires later.", "state your standards early. the right one won't be scared off."),
                    make_content("3) venting effectively, not obsessively.", "overanalyzing every text creates false narratives.", "my coach recommended the nafsy app to dump the brain fog so i can stay high value and present."),
                    make_content("4) willing to walk away at any moment.", "the strongest negotiating position is being able to leave.", "never be afraid to lose someone who isn't sure about you."),
                    make_content("5) believing the first red flag.", "it's not a mistake, it's a preview.", "when people show you who they are, believe them the first time."),
                ]
            ),
        ),
        (
            "Slideshow 5 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. refusing to help people who won't help themselves.", "you can't save everyone, and trying will drown you.", "stop investing in people who are committed to staying stuck."),
                    make_content("2) accepting disappointment from others.", "people will hate your boundaries because they benefited from your lack of them.", "let them be mad. stay firm anyway."),
                    make_content("3) regulating before communicating.", "reactive texts always lead to regret.", "i use the nafsy app to track my mood swings (coach's orders) so i only respond when i'm calm."),
                    make_content("4) refusing to justify my choices.", "\"i don't want to\" is a valid reason.", "you don't need their permission to live your life."),
                    make_content("5) walking away from gossip.", "participating in low-vibrational talk drains your spirit.", "protect your ears and your energy."),
                ]
            ),
        ),
        (
            "Slideshow 6 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. keeping other options open.", "hyper-focusing on one person creates desperation energy.", "rotate your roster until a commitment is made."),
                    make_content("2) not acting like a girlfriend.", "giving wife benefits at a talking stage price is a scam.", "don't cook, clean, or counsel until there is a title."),
                    make_content("3) managing the urge to stalk.", "checking their location or following count ruins your peace.", "my coach got me on the nafsy app to distract myself when i feel the urge to check up on them."),
                    make_content("4) accepting confusion as a \"no.\"", "clarity is attractive. confusion is manipulation.", "if you have to ask where you stand, you're not standing on solid ground."),
                    make_content("5) letting them initiate.", "if you are always the engine, the car stops when you stop.", "lean back and see if they step forward."),
                ]
            ),
        ),
        (
            "Slideshow 7 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. ghosting bad vibes immediately.", "you don't owe clarity to someone who disrespects you.", "protect your energy field ruthlessly."),
                    make_content("2) asking for space without guilt.", "solitude is where you reconnect with yourself.", "normalize taking days off from friendship."),
                    make_content("3) journaling before venting to friends.", "trauma dumping exhausts your support system.", "my coach loves the nafsy app for this—it helps me process the heavy stuff so i can be a better friend."),
                    make_content("4) not taking things personally.", "how people treat you is a reflection of them, not you.", "detach from their projection."),
                    make_content("5) forgiving myself for past mistakes.", "you did the best you could with what you knew.", "be as kind to yourself as you are to others."),
                ]
            ),
        ),
        (
            "Slideshow 8 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. ignoring their social media.", "watching their story 5 minutes after they post looks desperate.", "mute them. stay a mystery."),
                    make_content("2) not future tripping.", "planning the wedding on date three ruins the vibe.", "stay in the present moment. enjoy what is happening now."),
                    make_content("3) checking my attachment style.", "i used to get clingy when i felt insecure.", "my therapist recommended the nafsy app to understand my attachment triggers so i stay secure."),
                    make_content("4) having high standards, low expectations.", "know what you want, but don't expect them to be perfect.", "let them show you who they are naturally."),
                    make_content("5) never double texting.", "if they didn't reply, they saw it and chose not to.", "silence is a message. read it loud and clear."),
                ]
            ),
        ),
        (
            "Slideshow 9 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. stopping the over-apologizing.", "saying sorry for existing makes you look small.", "replace \"sorry\" with \"thank you for waiting.\""),
                    make_content("2) limiting time with family members who drain me.", "blood doesn't justify toxicity.", "love them from a safe distance."),
                    make_content("3) identifying my emotional burnout.", "i used to think i was just lazy, but i was exhausted.", "using the nafsy app helped me track my burnout patterns (coach's advice) so i can rest earlier."),
                    make_content("4) speaking up when something bothers me.", "silence is consent.", "say it even if your voice shakes."),
                    make_content("5) trusting my intuition over their logic.", "gaslighting makes you doubt your reality.", "if your gut says danger, listen."),
                ]
            ),
        ),
        (
            "Slideshow 10 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. being willing to lose them.", "desperation smells like cheap cologne.", "approach dating with an abundance mindset."),
                    make_content("2) not engaging in text marathons.", "save the conversation for the date.", "keep the mystery alive. text for logistics, not life stories."),
                    make_content("3) calming my nervous system before dates.", "showing up anxious makes the energy weird.", "i use the nafsy app (therapist tip) to do a quick check-in so i show up confident and chill."),
                    make_content("4) watching how they treat service staff.", "rudeness to waiters is a major red flag.", "character is how they treat people who can do nothing for them."),
                    make_content("5) keeping my options open until exclusivity.", "don't put all your eggs in one basket.", "until they ask you to be exclusive, you are single."),
                ]
            ),
        ),
        (
            "Slideshow 11 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. saying \"i need to think about it.\"", "you don't have to agree to requests immediately.", "buy yourself time to check your capacity."),
                    make_content("2) refusing to engage in arguments.", "peace is better than being right.", "silence is the best response to a fool."),
                    make_content("3) prioritizing my sleep over their crisis.", "staying up till 3am for their drama ruins my next day.", "my coach had me download the nafsy app to set mental cut-off times for my own health."),
                    make_content("4) not taking responsibility for their feelings.", "\"you made me mad\" is manipulation.", "you are only responsible for your intent, not their reaction."),
                    make_content("5) distancing myself from complainers.", "constant negativity rewires your brain.", "surround yourself with people who talk about ideas, not problems."),
                ]
            ),
        ),
        (
            "Slideshow 12 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. ignoring breadcrumbs.", "random likes and emojis are not effort.", "don't starve for attention so much that you eat crumbs."),
                    make_content("2) focusing on how i feel, not how they feel.", "do you even like them? or do you just like being liked?", "center your own experience."),
                    make_content("3) checking my compatibility, not just chemistry.", "butterflies can be a warning sign.", "my therapist suggested the nafsy app to log my dates and see if i'm ignoring compatibility for chemistry."),
                    make_content("4) letting go of the outcome.", "trying to control the result creates anxiety.", "trust that what is meant for you will not pass you."),
                    make_content("5) maintaining my boundaries.", "don't lower your fence just because they are cute.", "respect is the foundation of love."),
                ]
            ),
        ),
        (
            "Slideshow 13 - Emotional Boundaries",
            ensure_numbering_sequence(
                [
                    make_cover("5 emotional boundaries that felt selfish but saved me:", "(my nervous system coach taught me these)"),
                    make_content("1. cancelling plans when i'm burnt out.", "forcing myself to go out creates resentment.", "rest is productive. take the night off."),
                    make_content("2) muting people on social media.", "comparison is the thief of joy.", "curate your feed to support your mental health."),
                    make_content("3) dealing with my inner critic.", "negative self-talk is the ultimate boundary violation.", "i use the nafsy app (coach's recommendation) to rewrite my internal narrative."),
                    make_content("4) asking for what i need directly.", "expecting them to read your mind is unfair.", "clear communication prevents disappointment."),
                    make_content("5) refusing to be the \"bigger person.\"", "sometimes the bigger person needs to set a hard boundary.", "you don't have to tolerate disrespect to be mature."),
                ]
            ),
        ),
        (
            "Slideshow 14 - Talking Stage",
            ensure_numbering_sequence(
                [
                    make_cover("5 things i do in the talking stage to (almost) guarantee a relationship after:", "(take notes)"),
                    make_content("1. staying mysterious.", "don't tell them your whole life story on date one.", "oversharing creates false intimacy."),
                    make_content("2) watching their actions when they are angry.", "anger reveals their true character.", "if they scare you, leave."),
                    make_content("3) addressing my fear of abandonment.", "clinging too tight pushes them away.", "my coach told me to use the nafsy app to soothe my inner child when i feel abandoned."),
                    make_content("4) not making them my therapist.", "emotional dumping is heavy for a new connection.", "keep it light and fun in the beginning."),
                    make_content("5) knowing when to walk away.", "don't stay just because you've already invested time.", "sunk cost fallacy keeps you stuck in dead ends."),
                ]
            ),
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate 14 randomized slideshows from one image folder")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducible picks")
    parser.add_argument("--dry-run", action="store_true", help="Print chosen images without rendering output files")
    parser.add_argument("--only", type=int, choices=range(1, 15), help="Generate only one slideshow index (1-14)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rng = random.Random(args.seed)

    image_paths = list_images(IMAGE_DIR)
    image_metas = build_image_meta(image_paths)
    validate_inputs(image_metas)

    slideshows = build_slideshows()
    if args.only:
        slideshows = [slideshows[args.only - 1]]

    if not args.dry_run:
        OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

    usage_count: DefaultDict[Path, int] = defaultdict(int)

    for idx, (title, slides) in enumerate(slideshows, start=1 if not args.only else args.only):
        print(f"\n=== Generating show {idx:02d}: {title} ===")
        save_slideshow(
            show_idx=idx,
            title=title,
            slides=slides,
            rng=rng,
            images=image_metas,
            usage_count=usage_count,
            dry_run=args.dry_run,
        )

    print("\nDone.")


if __name__ == "__main__":
    main()
