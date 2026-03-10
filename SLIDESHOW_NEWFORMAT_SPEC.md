# Slideshow New-Format Specification

This document defines the final, approved slideshow pipeline and style for this project.
Use this as the source of truth for future edits.

## 1) Goal

Generate 6 text slideshows (5 slides each) with:

- one consistent visual style
- one image source folder
- clean readable text overlay
- balanced randomization with reduced repeats

## 2) Script and Core Files

- Generator script:
  - `/Users/azizmadhi/Apps/Social/generate_slideshows_talking_stage_6.py`
- Render engine:
  - `/Users/azizmadhi/Apps/Social/slideshow_tool.py`
- Output root:
  - `/Users/azizmadhi/Apps/Social/ready_to_post`

## 3) Image Source (Important)

Only this folder is used for all slides (hook + content):

- `/Users/azizmadhi/Apps/Social/raw_images/newforamt photos`

No `hook2`, no `demos`, no extra buckets for this pipeline.

Invalid/corrupt images are skipped automatically.
Known excluded corrupt file:

- `26fea4b7b81ca61b1ebd22c51c4d6bad.jpg`

## 4) Final Visual Style

### Hook slide (Slide 1)

- Title near top, centered.
- Subtitle under title, left-offset style (under title block).
- White text with subtle black stroke for readability.
- 3:4 output ratio.

### Content slides (Slides 2-5)

- Three centered text blocks:
  - numbered line
  - explanation line
  - closing line (no symbol prefix)
- White text with subtle black stroke for readability.
- 3:4 output ratio.

### Typography and Stroke (final)

From `generate_slideshows_talking_stage_6.py`:

- `cover_title`: `60`
- `cover_subtitle`: `31`
- `content`: `54`
- `stroke width`: `2`
- `stroke color`: black
- `fill`: white

Font variation override is intentionally NOT used.
The renderer uses default TikTok Sans behavior.

## 5) Text Normalization Rules

- Whitespace normalized.
- Numbering enforced for content slides:
  - `1)`, `2)`, `3)`, `4)`
- Any leading symbol on closing line is removed:
  - removes leading `✨`, `*`, `-`
- Closing line is plain text (no emoji/bullet marker).

## 6) Randomization and Repeat Control

Selection model:

- Randomized from a ranked candidate list.
- Ranking prioritizes globally least-used images first.
- Per slide, pick randomly from top 3 ranked candidates.
- No image repeats inside the same slideshow.

This gives variety while reducing over-repetition across the full batch.

## 7) Slideshow Structure

Total generated:

- 6 shows
- 5 slides per show
- folders:
  - `show_01_slideshow_1_emotional_boundaries`
  - `show_02_slideshow_2_talking_stage`
  - `show_03_slideshow_3_emotional_boundaries`
  - `show_04_slideshow_4_talking_stage`
  - `show_05_slideshow_5_emotional_boundaries`
  - `show_06_slideshow_6_talking_stage`

## 8) Commands

### Generate all 6 (recommended)

```bash
/Users/azizmadhi/Apps/Social/venv/bin/python /Users/azizmadhi/Apps/Social/generate_slideshows_talking_stage_6.py --seed 19
```

### Generate one show only

```bash
/Users/azizmadhi/Apps/Social/venv/bin/python /Users/azizmadhi/Apps/Social/generate_slideshows_talking_stage_6.py --only 6 --seed 19
```

### Dry run (no files written)

```bash
/Users/azizmadhi/Apps/Social/venv/bin/python /Users/azizmadhi/Apps/Social/generate_slideshows_talking_stage_6.py --dry-run --seed 19
```

## 9) Quick QA Checklist

After generation, verify:

- each `show_*` folder has exactly 5 files: `slide_01.jpg` to `slide_05.jpg`
- hook title/subtitle layout matches target
- content slides are centered in 3 blocks
- no symbol appears before closing line
- text is readable on bright areas

Quick count command:

```bash
find /Users/azizmadhi/Apps/Social/ready_to_post -maxdepth 1 -type d -name 'show_*' | sort | while read -r d; do c=$(find "$d" -maxdepth 1 -name 'slide_*.jpg' | wc -l | tr -d ' '); echo "$(basename "$d") $c"; done
```

## 10) Troubleshooting

### Text too heavy or too light

Adjust only these first:

- `STYLE_STROKE["width"]`
- `content` size in `CONTENT_STYLE_SIZES`
- `cover_title` and `cover_subtitle` in `HOOK_STYLE_SIZES`

### Font looks wrong

- Do not add custom `font_axes` override.
- Keep default TikTok Sans variation path.

### Sparkle/emoji renders as box

- Do not use sparkle prefix for closing line.
- Keep plain text closing line.

## 11) Change Policy

When changing style:

- update this document
- regenerate all 6 slideshows (not one show only) unless explicitly requested
- validate folder counts and sample visuals

