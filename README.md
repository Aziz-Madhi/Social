# 🎨 ScrollStop Carousel Generator

Welcome to the **ScrollStop Carousel Generator**! 🚀

This is a powerful, highly customizable, and completely **open-source** tool designed for content creators, social media managers, educators, and developers. It automates the creation of visually stunning carousel slideshows for platforms like Instagram, TikTok, and Pinterest. 

By leveraging intelligent text wrapping, outline-stroke rendering, and automated image-processing pipelines, this project helps you transform plain text insights into premium, high-converting social media carousels in seconds.

---

## 🌟 Key Features

* **📖 Interactive Web UI Dashboard**: A local Flask-based web application with a live previewer, real-time font adjustment sliders, and batch-saving capabilities.
* **✍️ Variable Font Support**: Native integration with variable font axes (such as **TikTok Sans**) supporting custom weights, widths, optical sizes, and slants to ensure clean, modern typography.
* **🖼️ Smart Image Processing**:
  * Automatic crop-to-aspect-ratio (3:4, 4:5, 9:16, 1:1, etc.).
  * High-quality upscaling via `LANCZOS` resampling.
  * Max-quality JPEG output (Chroma Subsampling = 4:4:4) to eliminate color bleeding around text outlines.
* **🛡️ High Contrast & Readability**: Subtly outlines all text with configurable stroke outlines to ensure readability over bright, colorful, or busy image backgrounds.
* **🎲 Smart Randomization & Deduplication**:
  * Prevents using duplicate background images within the same slideshow.
  * Incorporates a globally least-used image selection model, keeping your feed diverse and fresh.
  * Automated placeholder selection for specific slide sections (e.g., Hook slides, Content slides, and App Demo CTAs).
* **📦 Pre-configured Batch Generators**: Ready-to-use scripts tailored for generating topics like relationship boundaries, microhabits, anxiety symptoms, and app promotions (specifically integrated with **Nafsy** app assets).

---

## 📁 Directory Structure

```
/Social
├── venv/                       # Python virtual environment
├── fonts/                      # Open-source font files (.ttf)
│   └── TikTokSans-VariableFont_opsz,slnt,wdth,wght.ttf
├── raw_images/                 # Input photos divided into folders:
│   ├── hooks/                  # Attention-grabbing background images
│   ├── slides/                 # Core content background images
│   └── demos/                  # CTA/App preview screenshots (e.g., mood, chat)
├── ready_to_post/              # Output directory for processed slides
├── templates/                  # Flask HTML template directory (index.html)
├── static/                     # Web dashboard assets (app.js, styles.css)
├── config.json                 # Global configuration for text-sizes, spacing, and output quality
├── content.json                # JSON content for slideshow texts
├── slideshow_tool.py           # Core image processing and text overlay functions
├── auto_slideshow.py           # Single-show automated CLI script
├── create_slideshow.py         # Script showing how to build a manual slideshow step-by-step
├── generate.py                 # Unified generator script (reads config.json + content.json)
├── ui_app.py                   # Local Flask server script
├── Start_UI.command            # Double-clickable launch script for macOS users
├── activate.sh                 # Environment activation helper
└── requirements.txt            # Python dependencies (Pillow, Flask)
```

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have **Python 3.x** installed.

### 2. Setup the Environment
Clone or download this repository, activate the environment, and install dependencies:

```bash
# Activate virtual environment
source activate.sh

# Or manually:
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt
```

### 3. Run the Web Dashboard
You can launch the interactive web GUI to preview text placement and generate batches interactively:

* **On macOS**: Double-click `Start_UI.command`.
* **Via Terminal**:
  ```bash
  python ui_app.py
  ```

Then open your browser and navigate to: **`http://localhost:5050`**

---

## 🛠️ CLI Generation Workflows

The generator scripts can be run directly from the command line:

### Using the Unified Generator (Recommended)
You can define your content inside `content.json` and styles in `config.json`, then execute:
```bash
python generate.py
```
To run with custom config/content files:
```bash
python generate.py --config custom_config.json --content custom_content.json
```

### Running Batch Theme Generators
There are pre-compiled pipelines with preset content that target specific themes:
* **Nafsy App Promos (14 Slideshows)**:
  ```bash
  python generate_slideshows_nafsy_14.py
  ```
* **Talking Stage / Relationship Advice (6 Slideshows)**:
  ```bash
  python generate_slideshows_talking_stage_6.py --seed 19
  ```
* **Microhabits (14 Slideshows)**:
  ```bash
  python generate_slideshows_microhabits_14.py
  ```

---

## 🎛️ Customizing Layouts

You can change text styling, fonts, and spacings by modifying `config.json`. Below are key customization keys:

```json
{
  "font": {
    "cover_title": 50,          // Hook title font size
    "cover_subtitle": 38,       // Hook subtitle font size
    "content": 45,              // Content slide font size
    "optical_size": 36,         // Variable font optical size (opsz)
    "weight": 600               // Variable font weight (wght)
  },
  "stroke": {
    "width": 2,                 // Thickness of text outline
    "color": "black",           // Text outline color
    "fill": "white"             // Inner text color
  },
  "aspect_ratio": "3:4"         // Target aspect ratio (9:16, 4:5, etc.)
}
```

---

## 🤝 Open Source & Contributing

This project is proud to be **open source**! We believe in community-driven design, and we welcome contributions of any kind:

* **Reporting bugs** and suggesting features in Issues.
* **Submitting pull requests** to improve text-wrapping logic, support more variable fonts, or add new aspect ratios.
* **Adding new slide layouts** or templates to the dashboard.

Feel free to fork this project, modify the styling to match your brand, and build wonderful things! 

*Happy Creating!* 🎉
