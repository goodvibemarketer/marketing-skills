---
name: linkedin-carousel-builder
description: Turn an article or report into a branded LinkedIn carousel PDF (1080x1350) using your Claude Design System. Use for LinkedIn carousels, document posts or repurposing articles into slides.
---

# LinkedIn Carousel Builder

Repurposes one piece of long-form content (an article, blog post, report, whitepaper, newsletter issue or transcript) into a LinkedIn carousel: a multi-page **PDF document post** at 1080 × 1350 px per page (4:5 portrait), styled by the user's connected design system, ending with a CTA to follow the author or subscribe to their newsletter.

The PDF is the main deliverable. LinkedIn carousels are uploaded as documents, so one PDF with one slide per page is what the user posts. PNGs of each slide are a secondary output for previews and reuse.

---

## Make it yours (edit this block once)

This skill is built to be shared. Everything brand-specific comes from the design system, and everything author-specific comes from this block. Fill it in once after installing; leave a line blank to have Claude ask each time.

```yaml
author_name:            # e.g. Jane Smith
author_headline:        # e.g. B2B marketing lead · writes about AI in marketing
author_photo:           # file name or URL of a square headshot (optional)
linkedin_handle:        # e.g. /in/janesmith (optional)
default_cta:            # follow | newsletter
newsletter_name:        # e.g. The Friday Brief (if default_cta is newsletter)
newsletter_url:         # e.g. janesmith.substack.com (short, readable form)
newsletter_promise:     # one line on what subscribers get, e.g. one AI workflow every Friday
follow_promise:         # one line on why to follow, e.g. practical AI for B2B marketers, 3x a week
slide_count:            # default 8 (range 6-10)
voice_notes:            # optional, e.g. British spelling, no emoji, sentence case headlines
grid_background:        # on | off  (default on; see "Default visual signatures")
title_highlight:        # on | off  (default on; see "Default visual signatures")
```

If this block is empty and the conversation doesn't supply the details, ask once for: name, headline, CTA type (follow or newsletter), and the newsletter name + URL if relevant. Don't invent any of them.

---

## Step 1 · Gather the three inputs

1. **The source content.** An attached file (docx, pdf, md, txt), pasted text, or a URL. Read all of it before planning. If it's a URL that can't be fetched, ask the user to paste or attach it.
2. **The design system.** Claude Design's connected design system is the source of truth for colour, type, spacing, radius, components and logo. See Step 3.
3. **The author identity and CTA.** From the "Make it yours" block or the conversation.

## Step 2 · Plan the carousel before designing anything

Carousels fail on content, not styling. Do this thinking first and show the user the plan as a short slide-by-slide outline (one line per slide) when they're present; if they're not, proceed and include the outline with the delivery.

**Find the one controlling idea.** Write one sentence: the single claim or question the carousel carries. Every slide must serve it. A 3,000-word article usually contains four good carousels; pick the strongest one and leave the rest out.

**Extract, then resequence.** Pull the sharpest claims, numbers, frameworks, quotes and examples. Order them for a swipe, not in the article's order: hook → tension → payoff → proof → CTA.

**Compress hard.**
- Headlines are short phrases or one tight sentence, max ~10 words.
- Body copy max ~30 words per slide; most slides should have far less.
- One idea per slide. If a slide needs two headings, it's two slides.
- Keep the author's words and voice where they're strong; don't flatten them into generic marketing copy.
- Numbers keep their source. If a stat comes from a third party, name it on the slide in small type (e.g. "Source: Forrester, 2026").

**Never add facts, stats or quotes that aren't in the source.**

### Slide types (pick and order to suit the content)

| Type | Use it for | Anatomy |
|---|---|---|
| **Hook** (always slide 1) | stopping the scroll | the controlling idea as a bold claim, question or surprising number; one short subline; author footer. Largest type in the set. |
| **Tension** | why this matters now | the problem or shift, in one headline + one or two lines |
| **Big number** | a single striking stat | the number huge, one line of context, source in small type |
| **Chart** | a comparison or trend | a simple bar/line chart, one highlighted series in the accent colour, one-line takeaway |
| **List** | 3-5 points, steps, signs, mistakes | headline + short items; numbered if order matters |
| **Framework** | a model, process or before/after | a simple diagram (steps, 2x2, before → after) drawn in stroke-based line art |
| **Quote** | a line worth screenshotting | one statement centred with lots of space; attribution if it's someone else's |
| **Example** | proof it's real | a short worked example or case, with the outcome |
| **Summary** (optional, second to last) | the save-worthy recap | the 3-5 takeaways in one place |
| **CTA** (always last) | follow or subscribe | see Step 5 |

A typical 8-slide flow: Hook → Tension → Big number or Chart → List or Framework → Example → Quote → Summary → CTA. Vary slide types; never run three of the same type in a row.

**The hook decides everything.** Write three hook options, pick the strongest, and show the user the two alternatives on delivery so they can swap. Good hooks are specific (a number, a named shift, a contrarian claim); weak hooks are vague ("5 tips for better marketing").

**Pick the highlight word.** For each slide headline, choose the one word or short phrase (max 3 words) that carries the meaning. It gets the title highlight (see Default visual signatures), or the design system's own emphasis style.

## Step 3 · Apply the design system

**If a design system is connected in Claude Design** (or the project has a `design.md`, design tokens or CSS variables): map every visual decision to it. Background, surface, text, accent, borders, radius, spacing, type families and type scale all come from the system's tokens or components. Don't hardcode hex values or fonts that aren't in the system. Use the system's logo only where its usage rules allow.

**If no design system is found:** ask once: "Connect your design system in Claude Design, or share your brand URL or colours and fonts, and I'll use them." If the user wants to go ahead without one, or isn't there to answer, build with a neutral fallback (off-white background, near-black text, one muted accent, a clean serif or sans pairing) plus the default visual signatures below, and say clearly on delivery that it's unbranded and will restyle once a system is connected.

### Default visual signatures (the design system overrides these)

Two signature treatments ship with this skill. They are defaults, not brand rules: the connected design system always wins.

**Precedence, in order:**
1. If the design system defines its own **background treatment** (a texture, pattern, gradient, image or an explicit "plain background" rule), use that and drop the grid. If it defines its own **emphasis style for headline words** (a highlight, underline, colour-swap, italic or weight change), use that and drop the highlighter.
2. If the design system is silent on either, keep that signature but draw it **only in the design system's colours** (grid lines from its border/neutral token, highlight from its accent or highlight token).
3. If `grid_background` or `title_highlight` is set to `off` in the "Make it yours" block, leave that signature out entirely.

**1 · Notepad grid background.** A faint, architect-style square grid across the slide background, drawn with CSS repeating linear gradients. It should be felt more than seen.
```css
.slide {
  --grid-line: color-mix(in srgb, var(--color-border, #2B2624) 9%, transparent);
  --grid-size: 40px;
  background-color: var(--color-background, #F7F6F2);
  background-image:
    linear-gradient(to right,  var(--grid-line) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-line) 1px, transparent 1px);
  background-size: var(--grid-size) var(--grid-size);
}
```
Replace the `var(--color-...)` names with the design system's real token names; the hex values are only the neutral fallback. Keep grid opacity low (roughly 6-12%) so body text contrast is unaffected. Cards or panels on top of the grid use the system's surface colour so text never sits directly on busy lines.

**2 · Highlighter on the headline keyword.** An irregular, semi-transparent highlighter-pen band sitting behind the chosen highlight word, covering the body of the letters from just below the baseline to above the x-height, in each headline (always on the hook slide; on other headlines where it helps, not necessarily every slide). It should look hand-drawn: slightly uneven edges, not a perfect rectangle.
```html
<span class="hl">hands-off<svg class="hl-mark" viewBox="0 0 200 40" preserveAspectRatio="none" aria-hidden="true">
    <path d="M2 9 C 40 3, 90 8, 130 4 S 185 5, 198 8 L 197 34 C 150 38, 100 32, 60 36 S 15 37, 3 33 Z"/>
  </svg></span>
```
```css
.hl { position: relative; white-space: nowrap; z-index: 0; }
.hl-mark { position: absolute; left: -4%; width: 108%; bottom: 0.14em; height: 0.62em; z-index: -1;
           fill: var(--color-accent, #8B1A1A); opacity: 0.3; }
```
Rules: one highlight per headline, max 3 words, never across a line break (`white-space: nowrap`), text stays fully readable on top of it, and the mark uses the accent token at low opacity. Check it reads as a highlighter behind the letters, not an underline beneath them: the band should cover most of the lowercase letters' height. Nudge `bottom` and `height` for the headline font if needed. Set the fill on the `svg` itself (as above) so it still applies if the path is reused via `<use>`.

### Carousel-specific rules the design system doesn't cover
- **Canvas:** 1080 × 1350 px per slide. Keep a safe margin of ≥ 72 px on all sides; nothing but backgrounds crosses it.
- **Mobile legibility:** most views are on a phone. Body text ≥ 32 px, headlines ≥ 64 px, small labels (source lines, page numbers) ≥ 24 px. Contrast must stay readable on a small screen.
- **Accent is for meaning.** Use the accent colour on the one word, number or series that matters on each slide, not as decoration.
- **Lining numerals.** Set `font-variant-numeric: lining-nums` on the slides; many editorial serifs default to old-style figures that drop below the baseline in big numbers.
- **Clean top margin.** No eyebrow labels, category tags or running headers above the headline; the top of each slide leads straight into the title.
- **Consistent frame.** Same margins, footer, page indicator and swipe cue position on every slide so the set reads as one piece.
- **Line art over clip art.** Diagrams and icons are clean stroke-based vectors (round caps, one stroke weight), never stock icons or filled clip-art shapes.
- **Asymmetry over tiling.** Vary scale and layout between slides; avoid grids of identical boxes.
- **No emoji, no stock photos,** unless the user supplies images or the design system includes them.

### Footer (every slide except the CTA slide, which has its own treatment)
If the design system defines its own sign-off or footer component, use it as specified and place the page indicator and swipe cue wherever it leaves room. Otherwise:
Bottom-left: a small circular author photo (1:1, `border-radius: 50%`) if one was provided, next to the author name (bold) with the headline beneath it (smaller, secondary text colour). If the carousel is for a company page instead of a person, use the company logo per the design system's rules.
Bottom-right: page indicator (e.g. `3/8`) and, on slides 1 to n-1, a small swipe cue (an arrow or "swipe →").

## Step 4 · Build the slides

Build the slides as one HTML file, one `<section class="slide">` per slide, each exactly 1080 × 1350 px. If working in Claude Design, build them as frames/pages in the design using the design system's components, then produce the PDF (Claude Design's own PDF export is fine if it keeps each slide as one 1080 × 1350 page; otherwise use the pipeline below).

Keep shared values (margins, footer, type sizes, grid, highlight) as CSS variables or shared components so the user can ask for tweaks and every slide updates together.

## Step 5 · The CTA slide

The last slide asks for one thing. No swipe cue.

**Follow CTA:** a short line that restates the value of the carousel, the author photo larger (~200 px), name and headline, then "Follow [first name] for [follow_promise]".

**Newsletter CTA:** a short line that restates the value, the newsletter name prominent, the `newsletter_promise` in one line, and the `newsletter_url` in large readable type (links in PDF posts are not reliably clickable on LinkedIn, so the URL must be easy to read and type). Author name + photo small beneath.

## Step 6 · Render the PDF (and PNGs)

The PDF must have one page per slide, each exactly 1080 × 1350 px (810 × 1012.5 pt), with backgrounds printed.

CSS in the HTML:
```css
@page { size: 1080px 1350px; margin: 0; }
html, body { margin: 0; padding: 0; }
.slide { width: 1080px; height: 1350px; overflow: hidden; position: relative;
         break-after: page; page-break-after: always; }
.slide:last-child { break-after: auto; page-break-after: auto; }
```

Render with Playwright (Chromium). Use an installed Chromium if one exists; only run `playwright install chromium` if launching fails.
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
    page.goto("file:///path/to/carousel.html")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(500)
    # 1. the PDF (main deliverable)
    page.pdf(path="carousel.pdf", width="1080px", height="1350px",
             print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    # 2. one PNG per slide (secondary)
    for i, el in enumerate(page.query_selector_all(".slide"), 1):
        el.screenshot(path=f"slide-{i:02d}.png")
    browser.close()
```
PNGs come out at 2160 × 2700 (2x); downscale to 1080 × 1350 with Pillow if exact size is needed.

**Verify before delivering:** open the PDF (e.g. with `pypdf`) and check the page count equals the slide count and every page is 810 × 1012.5 pt. Then look at every slide image yourself: no text overflowing its box, no orphaned single words on headline lines, no awkward line breaks inside hyphenated words or numbers, highlights sitting behind their words like a highlighter (not an underline, not a solid black block), grid faint enough that text reads cleanly, footer and page numbers identical in position throughout. Fix and re-render until clean.

LinkedIn limits for document posts: max 100 MB and 300 pages; keep the file small by using real text (not images of text) in the PDF.

## Step 7 · Deliver

Give the user:
1. **The PDF** (named from the carousel's topic, e.g. `cmo-role-carousel.pdf`).
2. **The slide PNGs** or a contact sheet of all slides together for a quick look.
3. **A document title** for LinkedIn's upload field (short, it shows on the post).
4. **A post caption draft** in the author's voice: a hook line that isn't just the slide-1 headline repeated, 2-4 short lines of context, and a question or prompt to comment. If the source has a public URL, suggest posting it as the first comment rather than in the caption.
5. **The two alternative hooks** from Step 2.
6. **Any gaps** in one line each: fallback styling used, which default signatures were kept or overridden by the design system, missing author photo, stats that need a source checked.

## Self-audit (run before delivering)

- One controlling idea, and every slide serves it?
- Slide 1 is a specific, scroll-stopping hook?
- Every fact, number and quote traceable to the source, third-party stats labelled?
- All colours, fonts and spacing from the design system (or the fallback is flagged)?
- Grid and highlight: used only where the design system doesn't define its own background or emphasis style, drawn in the system's colours, and switched off if the config says off?
- One highlight per headline at most, reads as a highlighter behind the letters, never broken across lines?
- No eyebrow labels above headlines?
- Body text ≥ 32 px, headlines ≥ 64 px, labels ≥ 24 px; readable on a phone?
- Same margins, footer, page indicator on every slide; swipe cue on all but the last?
- CTA slide asks for exactly one thing (follow or subscribe) with a readable URL if newsletter?
- PDF page count = slide count, every page 1080 × 1350?
- Author details, newsletter name and URL match what the user provided, nothing invented?