---
name: linkedin-infographic-builder
description: Turns textual content into a single, polished infographic image (1080×1350 px PNG) utilizing Claude Design workflows. Dynamically handles company branding systems or personal LinkedIn avatars while enforcing clean, editorial anti-slop typography layouts.
---
# LinkedIn Infographic Builder

## Overview
Transforms textual content into one premium infographic image: a 1080×1350 px portrait PNG (4:5 ratio — the standard phone-feed format for Instagram and LinkedIn). The output is a single flat, high-fidelity image optimized for professional networks.

**Keywords**: infographic, visual summary, poster, carousel, shareable graphic, one-pager, brand-aligned graphic

## Design System & Branding Inheritance
This skill operates strictly within the context of a professional design ecosystem. Do not use random colors, default styling, or generic layouts.

1. **Token Detection:** Prioritize reading the local project's active `design.md` file or the workspace's default Claude Design System settings. Map all visual elements (backgrounds, containers, borders) to standard system tokens (e.g., `--color-primary`, `--radius-card`) rather than hardcoding static hex values.
2. **Fallback Trigger:** If no existing design tokens, CSS variables, or component definitions are detected in the environment, **halt generation immediately** and prompt the user: *"Please specify a target brand URL or upload your design system tokens to proceed."*

## Adaptive Footer Logic
Every infographic must feature a dedicated footer section that anchors the content. Dynamically adapt the footer layout to one of the following two contexts based on the user's target distribution channel:

*   **Company Brand Deliverables:**
    *   **Asset:** Place the company brand logo asset in the bottom-left of the footer.
    *   **Rules:** Maintain strict compliance with the logo padding, clear space, and scaling rules defined in the active design system.
*   **Personal LinkedIn Profile Posts:**
    *   **Asset:** Construct a 1:1 aspect ratio avatar container (`border-radius: 50%; overflow: hidden;`) in the bottom-left of the footer containing the user's profile picture asset.
    *   **Typography:** Pair the avatar inline with the user's Full Name (bold, primary text token) stacked directly above their professional headline/title (smaller, secondary text token).

## What "great" means here (Anti-AI Slop Guards)
AI engines naturally default to highly predictable layouts, identical grids, and uniform color distributions. Great design requires human intent:

- **Absolute Top-Margin Cleanliness (No Eyebrow Slop):** Do NOT include any "eyebrow text," categories, tags, tracking lines, or tagline labels (such as *"Field notes..."* or *"Assistants → agents → employees"*) above the main title banner. The absolute top of the canvas must feature a clean, generous, and uncrowded margin leading directly into the primary hero title.
- **One controlling idea.** State the single question the graphic answers or the single claim it makes. Everything on the canvas must serve that idea.
- **Three readable levels.** (1) The 2-second takeaway — the title or hero number. (2) The 10-second skim — section headers and labels. (3) The detail — read only if interested.
- **Asymmetrical & Custom Layouts:** Avoid dividing the canvas into perfectly identical boxes. Vary container sizes, use strategic negative space, and introduce diverse typography scaling to ensure the asset looks custom-crafted by a designer.
- **A deliberate reading path.** The layout must guide the eye intentionally (e.g., asymmetrical 2-column, hub-and-spoke, sequential timeline). It never just tiles content to fill space.

## Content craft
- **Compress hard.** Headers are noun phrases, not sentences. Body lines stay under ~12 words. Cut every word that doesn't change meaning.
- **Extract, then sequence.** Pull the key points, then order them by the reading path you chose — don't preserve the source's order by default.
- **Group, don't scatter.** Aim for 3–6 sections; more than ~8 distinct blocks is too dense for one image.
- **Lead with the payoff.** Put the takeaway near the top; supporting detail flows below it.

## Visual approach (Token-Driven)
- **Notepad Grid Background:** Style the base layout background container using a faint, clean, architect-style notepad grid line pattern. Generate this layout asset purely through CSS repeating linear gradients (`linear-gradient`) using light, subtle opacity system tokens.
- **Organic Title Highlighting:** Apply a distinct, irregular, semi-transparent marker brush stroke vector graphic element immediately underneath primary accent keywords within the main hero title to anchor visual hierarchy.
- **Clear Stroke-Based Line Art:** All custom graphical metaphors or layout icons (such as a minimalist tombstone silhouette or trend lines) must be rendered using clean, crisp vector stroke paths (`stroke-width`, `stroke-linecap: round`). Avoid heavy, solid, filled silhouette blocks or flat clipart shapes.
- **Color carries meaning, not decoration.** Pull your primary, secondary, and neutral colors directly from the design system tokens. Reserve accent states for hyper-specific callouts or semantic data states (positive/negative).
- **Maintain Data Visualization Flow:** Ensure macro arguments are driven by clear visual charts (like horizontal bar plots or trend graphs) placed prominently in the top third of the viewport. Do not replace intuitive data scales with plain text numbers if a chart serves the reading path better.
- **Establish a type scale.** Enforce a dramatic contrast in scale between the hero headline and body elements. Use the project’s defined font family stacks.
- **Canvas Margins:** Reserve a comfortable, protective margin (≈64–80 px) around the entire canvas edge where no layout text or structural containers may cross.

## Output: rendering the PNG (this part must be exact)
The deliverable defaults to a single flat PNG at **exactly 1080×1350 px**. Design in HTML/CSS mapped to the target size and rasterize with a headless browser. Recommended pipeline:

1. Build a self-contained HTML file with the body sized to exactly 1080×1350 px (`width: 1080px; height: 1350px; margin: 0; overflow: hidden;`).
2. Render to PNG with Playwright (Chromium) using a **deviceScaleFactor of 2** so the image text is perfectly crisp, then downscale or save to the exact target bounds.

```bash
pip install playwright --break-system-packages && playwright install chromium
```

```python
from playwright.sync_api import sync_playwright
from PIL import Image

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
    pg.goto("file:///home/claude/infographic.html")
    pg.screenshot(path="/home/claude/raw.png")
    b.close()

img = Image.open("/home/claude/raw.png").resize((1080, 1350), Image.LANCZOS)
img.save("/mnt/user-data/outputs/infographic.png")
print(img.size)  # must print (1080, 1350)
```

If Playwright is unavailable, fall back to building the canvas directly with Pillow at 1080×1350. Assert the final size is `(1080, 1350)` before presenting, and place the file in `/mnt/user-data/outputs/`.

## Before you finish — self-audit
- Did you verify if a `design.md` or system layout token profile was active?
- If it wasn't clear, did you pause to request the design system or target brand?
- Did you check that the top margin area is completely free of running headers, category text tags, or subtitle lines?
- Does the background accurately construct a subtle notepad-style grid pattern, and do the key header words use an organic highlighter mark?
- Are your graphical metaphors restricted strictly to crisp, stroke-based line art?
- Does the footer dynamically adapt to either a company logo layout or a circular LinkedIn profile avatar?
- Is the saved file exactly 1080×1350 px?
