---
name: linkedin-infographic-builder
description: Turns textual content into a single, polished infographic image (4:5 PNG, laid out at 1080×1350 and exported at 2× for sharp text) utilizing Claude Design workflows. Dynamically handles company branding systems or personal LinkedIn avatars while enforcing clean, editorial anti-slop typography layouts.
license: Complete terms in LICENSE.txt
---
# LinkedIn Infographic Builder

## Overview
Transforms textual content into one premium infographic image: a 4:5 portrait PNG (the standard phone-feed format for Instagram and LinkedIn), laid out at 1080×1350 CSS px and exported at 2160×2700 so text stays sharp on phones. The output is a single flat, high-fidelity image optimized for professional networks.

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
- **Scroll-stopping clarity.** The title names the subject in plain words (the product, company or thing) and says what's interesting about it. A stranger who hasn't read the source should know what it's about in two seconds. No abstract or clever titles that only make sense after reading. Write three options and pick the clearest.
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
- **Clear Stroke-Based Line Art:** All custom graphical metaphors or layout icons (such as a minimalist tombstone silhouette or trend lines) must be rendered using clean, crisp vector stroke paths (`stroke-width`, `stroke-linecap: round`). Avoid heavy, solid, filled silhouette blocks or flat clipart shapes. See **Hero illustration** below: every infographic has one.
- **Color carries meaning, not decoration.** Pull your primary, secondary, and neutral colors directly from the design system tokens. Reserve accent states for hyper-specific callouts or semantic data states (positive/negative).
- **Data drives a chart, and the data picks the chart.** When the source has numbers, show the main one as a chart, not as a number in a box. Choose the chart type from **Chart chooser** below. Bars are one option among many, not the default.
- **Establish a type scale.** Enforce a dramatic contrast in scale between the hero headline and body elements. Use the project’s defined font family stacks.
- **Canvas Margins:** Reserve a comfortable, protective margin (≈64–80 px) around the entire canvas edge where no layout text or structural containers may cross.

## Variety: pick the layout from the story

Infographics posted week after week must not look like the same template with new numbers. Before designing, pick **one layout archetype** that fits this story's shape, and sketch the reading path in a sentence.

| Archetype | Use when the story is… | Shape on the canvas |
| --- | --- | --- |
| **Hero metaphor** | one big idea with a strong image (a death, a race, a trap, a gate) | Title, then a large line-art illustration (35–45% of the canvas) with 2–4 annotations pointing at parts of it, then one supporting chart or stat |
| **Chart hero** | one dataset tells the story (a trend, a share, a gap) | Title, then one big chart (40–50% of the canvas) annotated directly, then 2–3 short takeaways |
| **Before / after split** | a change: old way vs new way, then vs now | Two columns or two rows with a strong divider; same structure on both sides so the difference jumps out |
| **Timeline / steps** | a sequence: how it happened, or what to do in order | Vertical or diagonal path with 3–6 nodes, illustration at the start or end |
| **Framework diagram** | a model: hub-and-spoke, 2×2 quadrant, pyramid, funnel, loop | The diagram is the hero; labels on the diagram, minimal body text |
| **Big number** | one figure is the story | One huge number with a small chart that gives it context (what it was before, what it's out of), then a short "so what" |
| **Scorecard** | comparing several options on the same criteria | A clean table or matrix with ticks, ratings or mini-bars; one row highlighted |

Rules:
- **Don't reuse a previous infographic's HTML as a starting point.** Start from a blank page and the chosen archetype. Shared pieces (grid background, highlighter, footer, CTA block) can be reused; the body layout cannot.
- **Rotate.** If a log of recent graphics exists (in the content engine: `runs/graphics-log.json`), don't use the same archetype as either of the last two, and don't use the same main chart type as the last one, unless the data really leaves no other honest choice. Add this graphic's archetype, chart type and hero illustration to the log when done.
- **Vary the furniture too:** don't always end on a dark band, don't always use two stat cards side by side, and change where the hero sits (top, middle, left half).

## Hero illustration

Every infographic has **one custom line-art illustration** that carries the controlling idea, drawn as inline SVG strokes in the brand's ink and accent colours. It is the thing people remember. (Reference: the tombstone on "The death of the CMO title".)

- **Find the metaphor in the headline.** Death → tombstone. Agents spending money → a robot hand holding a credit card. Ads arriving in chat → a chat bubble with a price tag. Hard to reach a human → a phone tree maze with a person at the centre. Engines that disagree → three compasses pointing different ways.
- **Size:** at least ~25% of the canvas in the Hero metaphor archetype; at least a 200×200 px spot illustration in the others. In Chart hero, the chart can be the hero, but add a small spot illustration near the title.
- **Style:** 2.5–4 px strokes, round caps and joins, mostly `--ink` with one accent colour for the part that matters. No fills except a light tint behind one element. No clipart, no emoji, no people's faces, no logos of real brands.
- **Annotate it.** Put labels or numbers on parts of the illustration where that helps (the date on the tombstone, the spend cap on the card).
- Draw it properly: build it from simple primitives, check it at 50% zoom, and redraw if it reads as a blob.

## Chart chooser

Pick the chart from what the numbers are, not from habit:

| The data is… | Use | Not |
| --- | --- | --- |
| Parts of one whole (2–4 parts, adding to 100%) | Donut or pie, max 4 slices, labels on the slices | Bars |
| One share of a group ("44% say…") | Waffle (10×10 squares, filled to the %) or a single ring | A lone number in a box, if space allows a chart |
| "X in 10 people" | Icon array of 10 simple figures | Pie |
| Change over time, 3+ points | Line chart with the last point labelled | Bars for each year |
| Two points in time (before → after) | Slope chart, or big arrow between two numbers | Two separate stat cards |
| Gap between two groups on one measure | Dumbbell (two dots on a line) or paired bars | Pie |
| Comparing several categories / ranking | Horizontal bar or lollipop, sorted | Pie |
| Composition across groups | 100% stacked bar | Several pies |
| Input → output (spend → sales) | Proportional shapes (small square vs large square) or a ratio arrow | Two bars |
| Stages that drop off | Funnel | Bars |
| A score or progress | Gauge or ring | Bars |

Chart rules: label values directly on the chart (no legends unless unavoidable); highlight the one data point that matters in the accent colour and keep the rest neutral; every chart has a one-line takeaway and a source line; draw charts as inline SVG so they're crisp; never invent or round numbers to make a chart work.

## Output: rendering the PNG (this part must be exact)
Design the layout at **1080×1350 CSS px** (4:5) and export the PNG at **2× : exactly 2160×2700 px**. Phones show a feed image about 400 points wide on screens with 3× pixel density, and platforms recompress what you upload, so a 1080-px file looks soft by the time it's on screen. A 2× file gives the platform more detail to scale down from, and text edges stay crisp. Same shape, same layout; LinkedIn, Substack and X all accept it (keep it under 5 MB; a flat-colour infographic is usually 1–1.5 MB).

1. Build a self-contained HTML file with the body sized to exactly 1080×1350 px (`width: 1080px; height: 1350px; margin: 0; overflow: hidden;`). All sizes in this Skill (type, margins, strokes) are in these CSS px.
2. Render with Playwright (Chromium) at **deviceScaleFactor 2** and save the screenshot as is. Don't downscale it.

```bash
pip install playwright --break-system-packages && playwright install chromium
```

```python
from playwright.sync_api import sync_playwright
from PIL import Image

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
    pg.goto("file:///path/to/infographic.html")
    pg.evaluate("document.fonts.ready")
    pg.screenshot(path="/path/to/infographic.png")
    b.close()

print(Image.open("/path/to/infographic.png").size)  # must print (2160, 2700)
```

If Playwright is unavailable, fall back to building the canvas directly with Pillow at 2160×2700 (every size doubled). Assert the final size is `(2160, 2700)` before presenting.

**Text must survive the phone.** The graphic is shown at roughly a third of its CSS size on a phone, so small type disappears first. In CSS px at the 1080 layout: no text under **20px** anywhere (source lines, captions, labels, footers included); body text and list items **22px or more**; text under 24px set in a **medium weight (500)**, never regular (400), because thin strokes blur first. If copy doesn't fit at these sizes, cut words, don't shrink type.

**Always keep the HTML next to the PNG.** Save the source as `<name>.html` beside `<name>.png` (e.g. `infographic.html` and `infographic.png`) and deliver both. Make it self-contained: embed fonts and images as data URIs, or reference them with paths relative to the HTML file, never absolute paths from this machine. Give each block a clear class name (`.headline`, `.hero`, `.chart`, `.cta`, `.footer`, and so on). The HTML is what lets the graphic be fixed and re-rendered later, or turned into an animated GIF with the infographic-animator Skill (Step 4b of the content engine). A PNG-only infographic can still be animated, but only with simple section fades.

## Before you finish — self-audit
- Did you verify if a `design.md` or system layout token profile was active?
- If it wasn't clear, did you pause to request the design system or target brand?
- Did you check that the top margin area is completely free of running headers, category text tags, or subtitle lines?
- Does the background accurately construct a subtle notepad-style grid pattern, and do the key header words use an organic highlighter mark?
- Are your graphical metaphors restricted strictly to crisp, stroke-based line art?
- Is there a hero illustration that carries the headline's idea, big enough to notice in the feed?
- Did the story pick the layout archetype, and is it different from the last two graphics?
- Is each chart the right type for its data (check the Chart chooser), with values labelled on the chart?
- Does the footer dynamically adapt to either a company logo layout or a circular LinkedIn profile avatar?
- Is the saved file exactly 2160×2700 px (the 1080×1350 layout at 2×)?
- Is every piece of text at least 20px (body 22px+), with anything under 24px in a medium weight (500)?
- Is the self-contained HTML saved next to the PNG, with clear class names on each block?
