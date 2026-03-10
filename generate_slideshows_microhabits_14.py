#!/usr/bin/env python3
import os
import random
import re
from slideshow_tool import process_slide

BASE_DIR = "/Users/azizmadhi/Apps/Social"
PHOTOS_DIR = os.path.join(BASE_DIR, "raw_images", "newforamt photos")
DEMO_EXERCISE_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "exercise")
DEMO_CHAT_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "chat")
DEMO_MOOD_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "mood")
DEMO_YEAR_DIR = os.path.join(BASE_DIR, "raw_images", "demos", "year view")
OUTPUT_ROOT = os.path.join(BASE_DIR, "ready_to_post")
ASPECT_RATIO = "3:4"

HOOK_TITLE = "5 micro-habits that helped me go from insecure to confident:"

VALID_EXTS = (".jpg", ".jpeg", ".png", ".webp")


def list_images(folder):
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if not f.startswith(".") and f.lower().endswith(VALID_EXTS)
    ]


def pick_random(folder):
    imgs = list_images(folder)
    if not imgs:
        raise RuntimeError(f"No images found in {folder}")
    return random.choice(imgs)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:50]


def make_cover():
    return {"type": "cover", "texts": {"title": HOOK_TITLE}}


def make_content(title: str, body: str):
    return {"type": "content", "texts": {"title": title, "body": body, "reality": None}}


SLIDESHOWS = [
    (
        "Social Confidence",
        "Mindfulness/Grounding",
        [
            make_cover(),
            make_content(
                "1. i stopped looking at the ground",
                "it felt safer to look down or at my phone, but it made me look small. now i look straight ahead and it instantly changes how people treat me.",
            ),
            make_content(
                '2. i stopped asking "does that make sense?"',
                "i used to say this because i was terrified of being misunderstood. now i just finish my thought and trust that i spoke clearly.",
            ),
            make_content(
                "3. i do a 3-minute breathing exercise before events",
                "right before i walk into a party, i sit in my car and do a quick grounding session on my phone. it resets my nervous system so i don't walk in with shaky energy.",
            ),
            make_content(
                "4. i started going to places alone",
                "sitting in a coffee shop by myself without headphones proved to me that i don't need a crutch to be okay in public.",
            ),
            make_content(
                "5. i stopped rushing to fill the silence",
                "awkward pauses used to terrify me. now i let the silence sit. it makes me seem calm even when i'm actually nervous.",
            ),
        ],
    ),
    (
        "Self-Worth",
        "Mood Tracking",
        [
            make_cover(),
            make_content(
                '1. i replace "sorry" with "thank you"',
                'instead of saying "sorry i\'m late," i say "thank you for waiting." it shifts the whole dynamic from guilt to gratitude.',
            ),
            make_content(
                "2. i accept compliments without deflection",
                'when someone said "nice shirt," i used to say "oh it\'s old and cheap." now i just say "thank you." don\'t reject the love people give you.',
            ),
            make_content(
                "3. i track my mood every morning",
                'i used to think i was just "crazy" or emotional all the time. logging it daily showed me i actually have patterns and i can handle them.',
            ),
            make_content(
                "4. i dress for the person i want to be",
                'i stopped saving my "good outfits" for special occasions. if i want to feel powerful on a random tuesday, i wear the blazer.',
            ),
            make_content(
                "5. i keep small promises to myself",
                "if i say i'm going to drink water, i do it. confidence is really just trusting yourself to do what you say you will do.",
            ),
        ],
    ),
    (
        "Emotional Control",
        "Venting/Validation",
        [
            make_cover(),
            make_content(
                "1. i lower my speaking volume",
                "i realized i was speaking fast and loud to ensure i was heard. now i slow down and lower my pitch. it signals that what i say is worth waiting for.",
            ),
            make_content(
                '2. i define the "worst case scenario"',
                'when i\'m scared, i write down exactly what happens if i fail. usually, the answer is "i\'ll be embarrassed for 5 minutes." once i see that, the fear disappears.',
            ),
            make_content(
                "3. i validate my feelings before i react",
                "when i feel triggered, i open my phone and just vent it all out privately first. it makes me feel seen so i can reply to people calmly later.",
            ),
            make_content(
                "4. i celebrate small wins",
                "every time i do the dishes or send a scary email, i mentally high-five myself. it builds a reputation with myself that i am capable.",
            ),
            make_content(
                "5. i walk with purpose",
                "even if i'm just going to the copier, i walk like i have a strict deadline. people naturally clear the way for someone who looks like they know where they are going.",
            ),
        ],
    ),
    (
        "Boundaries",
        "Mood Tracking",
        [
            make_cover(),
            make_content(
                '1. i stopped over-explaining my "no"',
                'i used to make up elaborate lies to get out of plans. now i just say "i can\'t make it." i realized i don\'t owe anyone an explanation for my time.',
            ),
            make_content(
                "2. i mute people who make me feel bad",
                "if seeing their story makes me feel jealous or insecure, they get muted. protecting my peace is more important than being polite on social media.",
            ),
            make_content(
                "3. i log my mood to understand my triggers",
                "i noticed i always felt insecure on sundays. seeing that pattern on my phone helped me plan for it so it doesn't ruin my week.",
            ),
            make_content(
                "4. i gatekeep my morning routine",
                "i don't check social media for the first 20 minutes of the day. it puts me in the driver's seat of my day instead of reacting to everyone else.",
            ),
            make_content(
                "5. i take up physical space",
                "i stopped crossing my legs and arms into a tiny ball. physically opening up my posture tricks my brain into feeling safe.",
            ),
        ],
    ),
    (
        "Presence & Charisma",
        "Mindfulness/Grounding",
        [
            make_cover(),
            make_content(
                "1. the 3-second eye contact rule",
                "when walking down the street, i look people in the eyes until they look away first. it helps me realize that other people are just as nervous as i am.",
            ),
            make_content(
                "2. i ask more questions",
                "insecurity makes me worry about what i'm going to say next. now i just ask people about themselves. it takes the pressure off me entirely.",
            ),
            make_content(
                "3. i use a quick grounding tool when i panic",
                "if i feel my heart racing in public, i step aside and use a 3-minute exercise on my phone. it stops the spiral before anyone else even notices i was anxious.",
            ),
            make_content(
                "4. i stopped fidgeting",
                "i used to play with my hair or rings constantly. being still sends a massive signal of confidence to everyone in the room.",
            ),
            make_content(
                "5. i smile first",
                "i used to wait for people to smile at me. being the one to break the ice makes me feel like the leader of the interaction.",
            ),
        ],
    ),
    (
        "Self-Respect",
        "Venting/Validation",
        [
            make_cover(),
            make_content(
                "1. i stopped self-deprecating",
                'making jokes about how "messy" i was didn\'t make me relatable, it made me insecure. i decided to stop bullying myself in front of other people.',
            ),
            make_content(
                "2. i buy myself the flowers",
                "i stopped waiting for someone else to treat me well. treating myself with respect forces me to set a higher standard for everyone else.",
            ),
            make_content(
                "3. i talk it out before i spiral",
                "instead of bottling things up, i use an app to vent my raw thoughts immediately. getting it out of my head stops me from overthinking it all day.",
            ),
            make_content(
                "4. i forgive myself quickly",
                "if i say something awkward, i don't replay it for 3 days. i remind myself that everyone is thinking about themselves, not me.",
            ),
            make_content(
                "5. i trust my gut intuition",
                'if a situation feels off, i leave. i stopped trying to be "nice" at the expense of my own comfort.',
            ),
        ],
    ),
    (
        "Breaking Anxiety",
        "Mood Tracking",
        [
            make_cover(),
            make_content(
                "1. i stopped checking my phone in public",
                "using my phone as a shield made me look unapproachable. now i just look around. it forces me to get comfortable in the moment.",
            ),
            make_content(
                '2. i reframe "nervous" as "excited"',
                'the physical feeling is almost the exact same. telling myself "i\'m excited" changes the energy from fear to anticipation.',
            ),
            make_content(
                "3. i track my mood cycles",
                "i realized i get anxious at the same time every month. knowing it's a pattern helps me be kinder to myself when it happens.",
            ),
            make_content(
                "4. i focus on the other person",
                "when i'm feeling self-conscious, i focus entirely on the person talking to me. you can't be self-conscious if you aren't thinking about yourself.",
            ),
            make_content(
                '5. i stand in the "doorframe pose" before entering a room',
                "i roll my shoulders back and chin up. your body language dictates how your mind feels.",
            ),
        ],
    ),
    (
        "Authentic Living",
        "Mindfulness/Grounding",
        [
            make_cover(),
            make_content(
                "1. i admit when i don't know things",
                'pretending to know things made me feel like an imposter. saying "i don\'t know, teach me" is actually a huge power move.',
            ),
            make_content(
                "2. i stopped trying to be perfect",
                "perfectionism is just fear in a fancy coat. i embrace being messy and human. people connect with that way more anyway.",
            ),
            make_content(
                "3. i take mental resets during the day",
                "when the world gets too loud, i take 5 minutes to do a mindfulness exercise. it helps me detach from the chaos and find my center again.",
            ),
            make_content(
                "4. i wear what i want",
                "i stopped dressing for the male gaze or for trends. i dress for what makes me feel like me. comfort is confidence.",
            ),
            make_content(
                "5. i voice my needs",
                'i stopped hoping people would read my mind. saying "i need a minute" or "i need a hug" changed my relationships.',
            ),
        ],
    ),
    (
        "Taking Action",
        "Venting/Validation",
        [
            make_cover(),
            make_content(
                "1. i do one thing that scares me weekly",
                "it could be sending an email or going to a new class. exposure therapy is real. the more you face fear, the smaller it gets.",
            ),
            make_content(
                "2. i make the first move in friendships or networking",
                "i stop waiting to be chosen. i introduce myself first. it puts the control back in my hands.",
            ),
            make_content(
                "3. i vent without judgment",
                "i use my phone to talk through my problems before i bring them to my friends. it helps me process my emotions so i don't dump them on other people.",
            ),
            make_content(
                "4. i finish what i start",
                "leaving things half-done made me feel flaky. completing tasks gives me proof that i am capable and reliable.",
            ),
            make_content(
                "5. i stopped gossiping",
                "talking bad about others came from my own insecurity. stopping that habit instantly made me feel cleaner and more secure in myself.",
            ),
        ],
    ),
    (
        "Inner Dialogue",
        "Mood Tracking",
        [
            make_cover(),
            make_content(
                "1. i talk to myself like a best friend",
                "i would never tell my friend she looks stupid. so i stopped saying it to myself in the mirror. be on your own team.",
            ),
            make_content(
                "2. i define my own success",
                "i stopped comparing my chapter 1 to someone else's chapter 20. focusing on my own lane removed 90% of my insecurity.",
            ),
            make_content(
                "3. i started logging my emotions",
                "seeing my mood on a graph made me realize my feelings are temporary. it stops me from spiraling when i'm having a bad day.",
            ),
            make_content(
                "4. i respond, i don't react",
                "i take a literal pause before replying to difficult questions. it gives me time to think and makes me look more composed.",
            ),
            make_content(
                "5. i embrace the cringe",
                "if i do something embarrassing, i laugh about it. if you can laugh at yourself, nobody can use it against you.",
            ),
        ],
    ),
    (
        "Calm Confidence",
        "Mindfulness/Grounding",
        [
            make_cover(),
            make_content(
                "1. i slowed down my movements",
                "frantic, jerky movements show anxiety. moving deliberately makes me feel like i own the space i'm in.",
            ),
            make_content(
                "2. i listen more than i talk",
                "i used to think i had to prove myself by talking constantly. now i listen. the quietest person in the room is often the most confident.",
            ),
            make_content(
                "3. i prioritize my mental state before big meetings",
                "i use a breathing tool to get grounded. i can't perform well if my mind is racing, so i fix that first.",
            ),
            make_content(
                "4. i maintain good posture",
                "slouching is a physical apology for existing. standing tall helps me breathe better and feel stronger.",
            ),
            make_content(
                "5. i don't seek validation",
                'i stopped asking "was that okay?" after i do something. i decide if it was okay. i validate myself.',
            ),
        ],
    ),
    (
        "Relationship to Self",
        "Venting/Validation",
        [
            make_cover(),
            make_content(
                "1. i stopped acting helpless",
                "if i don't know how to do something, i google it or figure it out. solving my own problems makes me feel incredibly capable.",
            ),
            make_content(
                "2. i romanticize my life",
                "i treat my morning coffee like a ritual. treating my life like a movie makes me feel like the main character.",
            ),
            make_content(
                "3. i express my emotions freely",
                "i use an app to vent when i'm sad instead of bottling it up. feeling my feelings is the only way to let them go.",
            ),
            make_content(
                "4. i set boundaries with my time",
                "i don't answer work emails at 9pm. respecting my own time teaches others to respect it too.",
            ),
            make_content(
                "5. i stopped stalking exes",
                "checking on them only kept me stuck in the past. blocking them gave me the freedom to move forward.",
            ),
        ],
    ),
    (
        "The Mindset Shift",
        "Mood Tracking",
        [
            make_cover(),
            make_content(
                '1. i stopped "mind reading"',
                "i used to assume everyone was judging me. now i remind myself i can't know what they think, so i stop guessing.",
            ),
            make_content(
                "2. i own my quirks",
                "instead of hiding my weird hobbies, i talk about them openly. authenticity attracts the right people and repels the wrong ones.",
            ),
            make_content(
                "3. i track my daily mood",
                "it helps me see that my anxiety is usually linked to lack of sleep or stress. understanding the cause makes the feeling less scary.",
            ),
            make_content(
                "4. i practice gratitude",
                "insecurity focuses on what i lack. gratitude focuses on what i have. it shifts my mindset instantly.",
            ),
            make_content(
                '5. i stopped waiting to be "ready"',
                "i realized i will never feel 100% ready. i do it scared. confidence comes after you take the action, not before.",
            ),
        ],
    ),
    (
        "Simplicity",
        "Mindfulness/Grounding",
        [
            make_cover(),
            make_content(
                "1. i uninstalled editing apps",
                "i stopped editing my body in photos. getting used to my real face online helped me love my real face offline.",
            ),
            make_content(
                '2. i say "i don\'t want to"',
                "i stopped making up excuses. honesty is scary but it builds so much self-respect.",
            ),
            make_content(
                "3. i take breathing breaks when i feel overwhelmed",
                "i pause and do a short breathing exercise on my phone. it separates me from the chaos for a moment.",
            ),
            make_content(
                "4. i stopped competing",
                "i remind myself there is enough space for everyone to win. someone else's beauty or success doesn't take away from mine.",
            ),
            make_content(
                "5. i let go of control",
                "i focus only on what i can control (my actions) and let go of the rest. trying to control others is the root of all my insecurity.",
            ),
        ],
    ),
]


MOOD_TRACKING_ALTERNATION = {
    2: DEMO_MOOD_DIR,
    4: DEMO_YEAR_DIR,
    7: DEMO_MOOD_DIR,
    10: DEMO_YEAR_DIR,
    13: DEMO_MOOD_DIR,
}


def demo_dir_for(slideshow_index: int, feature: str) -> str:
    if feature == "Mindfulness/Grounding":
        return DEMO_EXERCISE_DIR
    if feature == "Venting/Validation":
        return DEMO_CHAT_DIR
    if feature == "Mood Tracking":
        return MOOD_TRACKING_ALTERNATION.get(slideshow_index, DEMO_MOOD_DIR)
    raise RuntimeError(f"Unknown feature: {feature}")


def build_image_sequence(slideshow_index: int, feature: str, slide_count: int):
    if slide_count != 6:
        raise RuntimeError("Each slideshow must have exactly 6 slides")

    demo_dir = demo_dir_for(slideshow_index, feature)

    photos = list_images(PHOTOS_DIR)
    if not photos:
        raise RuntimeError(f"No images found in {PHOTOS_DIR}")

    if len(photos) >= 5:
        picked = random.sample(photos, 5)
    else:
        picked = [random.choice(photos) for _ in range(5)]

    demo_image = pick_random(demo_dir)

    return [picked[0], picked[1], picked[2], demo_image, picked[3], picked[4]]


def save_slideshow(index: int, title: str, feature: str, slides):
    folder_name = f"show_{index:02d}_{slugify(title)}"
    out_dir = os.path.join(OUTPUT_ROOT, folder_name)
    os.makedirs(out_dir, exist_ok=True)

    image_sequence = build_image_sequence(index, feature, len(slides))

    for i, (img_path, slide) in enumerate(zip(image_sequence, slides), 1):
        output_path = os.path.join(out_dir, f"slide_{i:02d}.jpg")
        process_slide(
            img_path,
            output_path,
            slide["type"],
            slide["texts"],
            aspect_ratio=ASPECT_RATIO,
        )


def main():
    if len(SLIDESHOWS) != 14:
        raise RuntimeError(f"Expected 14 slideshows, got {len(SLIDESHOWS)}")

    for idx, (title, feature, slides) in enumerate(SLIDESHOWS, 1):
        save_slideshow(idx, title, feature, slides)


if __name__ == "__main__":
    main()
