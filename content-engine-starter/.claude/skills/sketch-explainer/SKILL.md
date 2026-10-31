---
name: sketch-explainer
description: Turns one strategy, tactic, framework or idea into a hand-drawn "pen on paper" explainer image (handwritten title, wobbly boxes and arrows, highlighter on the key words, doodle icons, one punchline), the kind of simple visual that gets saved and shared on LinkedIn. Use when repurposing an article, report or post into a sketch-style graphic, for Substack Notes, X or LinkedIn, or when asked for a "hand-drawn", "sketch", "napkin" or "whiteboard" style image.
---

# Sketch explainer

Makes the opposite of the branded infographic: an image that looks drawn by hand in a notebook. Its job is to take **one** idea and make it obvious in a glance. Popular examples are a 2×2 ("what should I turn into an AI agent?"), a this-vs-that ("GPT wrapper vs agent harness") and a short numbered list that funnels into one line ("Hormozi's 3 lead magnet rules").

The text on the image is real text set in handwriting fonts, so it's always exact and sharp. Every line around it (boxes, circles, arrows, braces, highlighter, doodles) is drawn by `assets/sketch.js` with rough.js, so no two strokes are perfectly straight.

## Make it yours (edit this block once)

This Skill is built to be shared. Fill this in once after installing so every sketch fits your brand and your audience. Leave a line blank and Claude uses the default or asks.

```yaml
signature:        # small handwritten line bottom right, e.g. "Jane Smith · acme.com"; blank = no signature
pen:              # red | coral | blue | ink, or a hex code from your brand (default red)
marker:           # teal | yellow | green | pink, or a hex code from your brand (default yellow)
audience:         # who the sketches are for, e.g. heads of finance at UK SMEs
voice_notes:      # e.g. British spelling, lowercase titles, no emoji
```

Read this block before writing. Pass `signature` to the render script as `--sig`, and `pen` and `marker` as `--pen` and `--marker` (hex codes work too). Use `audience` to decide which idea in the source is worth drawing.

## What makes these work (keep to all of it)

- **One idea, one structure.** Pick the single framework, contrast or sequence in the source. If it needs two structures, it's two images.
- **Very few words.** Title ≤ 8 words. Each line ≤ 7 words. 25–60 words on the whole image. Write it like notes on a whiteboard, not sentences from the article.
- **The title asks or names.** A question the image answers ("who does what with AI?") or the thing being compared ("novice vs expert with AI"). Lowercase is fine and looks more hand-made. It must still name its subject (the stranger test: someone who hasn't seen the source reads only the title. Do they know what it's about?).
- **A subtitle that says what the reader gets,** e.g. "3 steps to using your domain expertise to build with AI". Never the source's name ("from Wicked Smart") or a vague label: it's a method or a finding, so say which.
- **A punchline at the bottom** that the whole drawing leads to, underlined or boxed. It must make sense on its own to someone who only sees the image, and state the takeaway the evidence on the image supports (a versus of give-up rates ends on "experts have the patience to keep going after AI gets it wrong", not on a line lifted from the article that needs its context, like "experts aren't better prompters").
- **Three colours at most:** ink, one pen colour (red by default) and one highlighter. Highlight only the 1–3 words per block that carry the meaning.
- **White space.** Leave a third of the page empty. Cramped sketches look like slides.
- **Facts only from the source.** No invented numbers, quotes or claims, and don't put words in the source's mouth (a "novice vs expert" contrast may only list what the source says about each side).

## Layouts (pick by the shape of the idea)

| Shape of the idea | Layout | Markup to use |
| --- | --- | --- |
| Steps, rules, a checklist | **List**: circled numbers, highlights, a brace into the conclusion, boxed punchline | `.num`, `.hl`, `[data-brace="down"]`, `[data-box]` |
| Old way vs new way, A vs B | **Versus**: two columns, a hand-drawn rule between them, an icon per row, punchline underlined | `.cols2` + `.divider-v`, `.icon[data-icon]` |
| Two dimensions, "which bucket is it in?" | **Matrix**: 2×2 with axis arrows or row/column labels; the quadrant that matters shaded in pen | `.matrix[data-lines]`, `.axes`, `[data-box="pen"][data-fill="hachure"]`, `.check` |
| A process or cause → effect | **Flow**: 3–5 boxes or icons joined by arrows | `[data-box]`, `[data-arrow="#next"]` |
| A formula or recipe | **Equation**: A + B = C with each term boxed or circled | `[data-circle]`, `.huge` |
| One striking stat or quote | **Big note**: the number or line huge, one doodle, a short caption | `.huge`, `.icon.l`, `.ul2` |

Working examples (HTML and rendered PNG) are in `examples/`: `list`, `versus` and `matrix`. Read the one closest to your idea before writing; don't copy its content.

## Markup (all in `assets/sketch.js`)

- Type: `.title` (big handwriting), `.subtitle`, `.big`, `.huge`, `.small`, `.caps` (marker capitals), `.pen` (red text), `.soft` (pencil grey), `.punch` (the bottom line).
- Layout: `.body` (fills and centres the middle), `.row`, `.col`, `.grow`, `.gap-s/m/l`, `.cols2`, `.matrix`, `.center`.
- Drawing: `.hl` highlighter · `.ul` / `.ul2` underline (`data-color="pen|ink|blue|marker"`) · `[data-box]` box (`="pen"` for red, `data-fill="hachure"` to shade, `data-pad`) · `[data-circle]` · `.num` circled number · `.check` ticked box · `[data-brace="right|down"]` · `[data-arrow="#id"]` · `.divider-v` / `.divider-h` (`data-dash`) · `.axes` · `.matrix[data-lines]` · `--frame` double border (render option).
- Doodles: `<span class="icon" data-icon="NAME"></span>` (`.s`, `.l` sizes). Names: robot, bubble, box, bars, trend, doc, bulb, target, person, people, clock, magnet, warning, coin, gear, mail, calendar, search, pencil, bolt, heart, tick, cross, funnel, layers, cycle, star, flag, money, chat, key, lock, globe, rocket. Use 0 or 3–6 icons, never 1–2 stray ones; same size within a column.

Minimum sizes (layout px): body text 30px+ (the base is 34px), labels 28px+. The page is exported at 2×.

## Render

Write only the inside of the page to an HTML file (title, `.body`, punchline), then:

Run the script from this Skill's folder (it sits next to this file). It needs Python with Playwright; install them first if they're missing (`pip install playwright` then `playwright install chromium`).

```bash
python3 scripts/render.py BODY.html OUT.png \
  --size portrait|square|landscape --seed N --pen red|coral|blue|#hex --marker teal|yellow|green|#hex \
  [--frame] [--sig "Jane Smith · acme.com"]
```

- Sizes: `portrait` 1080×1350 (LinkedIn, Substack, default), `square` 1080×1080 (X, Notes), `landscape` 1280×960. PNGs come out at 2× (e.g. 2160×2700).
- Use your brand colours from **Make it yours**, or `yellow` and `green`, which look most like a classic highlighter. One marker colour per image.
- The seed fixes the wobble, so a re-render looks the same. Change it to get a different hand.
- With `--sig`, a small handwritten signature goes bottom right. No other CTA on these images, so one image works unchanged on LinkedIn, X and Substack.
- **Every post that carries a sketch links to the source** underneath it: the LinkedIn first comment, a reply on X, or a "Full article:" line at the end of a Substack Note.
- The script prints `WARN` for unknown icons and for anything near the page edge.

## Check before using

Look at the PNG. Fix and re-render if: any text overflows or crowds a line, a highlight or underline misses its words, a box or brace cuts through text, the page looks more than two-thirds full, there are more than three colours, the title doesn't name its subject, or any word on it isn't supported by the source.

## Using it in a content plan

- Vary the layout: don't use the same one twice in a row.
- Square suits X and Substack Notes; portrait suits LinkedIn.
- Keep a simple log of what you made (date, layout, marker) so the mix stays varied.
