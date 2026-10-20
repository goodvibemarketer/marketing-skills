---
name: notebook-notes
description: Turns an article's framework, findings, process or rules into a photo-style page of handwritten notebook notes (ruled, dotted or grid paper, spiral or gutter binding, neon highlighter blobs, coloured pen underlines, circled numbers, arrows, pyramids), lying on a desk. Use when repurposing content into a "notepad", "notebook", "handwritten notes" or "bullet journal" style image for LinkedIn, X or Substack.
---

# Notebook notes

Makes an image that looks like a photo of someone's notebook page: the kind of handwritten breakdown that gets saved on LinkedIn ("The 5 P's", "11 habits", "7 rules", a layered pyramid, one idea fanning out to many). It sits between a polished branded infographic and a minimal pen sketch on blank paper.

How it differs from a minimal sketch:
- **It's a page in a real notebook.** Ruled, dotted or grid paper; spiral holes or a centre-fold gutter; the page sits slightly askew on a desk with a soft shadow.
- **Handwriting sits on the ruled lines.**
- **It holds more.** 6–11 numbered points each with a one-line explanation, or a process with notes beside each step. 60–140 words.
- **More colour, used like stationery:** one coloured pen (green, blue or red) for headings and underlines, and a neon highlighter for blobs and pyramid layers.
- **No signature, no footer, no CTA.** The image is just the page. The post links to the source instead (see Posting).

## Make it yours (edit this block once)

This Skill is built to be shared. Fill this in once after installing so every page fits your brand and your audience. Leave a line blank and Claude picks a varied default.

```yaml
pen:              # green | blue | red | ink, or a hex code from your brand
marker:           # yellow | orange | green | pink, or a hex code from your brand
favourite_looks:  # optional, e.g. ruled paper, spiral binding, wood desk
audience:         # who the pages are for, e.g. heads of finance at UK SMEs
voice_notes:      # e.g. British spelling, sentence case
```

Read this block before writing. Pass `pen` and `marker` to the render script (hex codes work too). Use `audience` to decide which points from the source make the page.

## Layouts (pick by the shape of the content)

| Content | Layout | Markup |
| --- | --- | --- |
| Rules, findings, habits, tips (6–11) | **Numbered notes**: one or two columns; each point a short underlined heading plus 1–2 lines | `.cols2`, `.num`, `.h`, `.ul` (`data-color="pen|ink"`) |
| A process or story in stages | **Mind-map flow**: stage names in highlighter blobs, notes under each, arrows from stage to stage, the outcome boxed at the bottom | `.blob[data-blob=outline]`, `[data-arrow="#next"]`, `[data-box]` |
| One thing that becomes many | **Hub**: one boxed idea, arrows fanning out to 3–5 boxes, a note and checklist below | `[data-arrow="#a,#b,#c"]`, `[data-box="pen"]`, `.check` |
| A stack of levels or priorities | **Pyramid**: 3–5 coloured layers, label + short line in each, a note at the apex | `.pyramid` > `.layer[data-fill=yellow|green|pink|blue|orange]` (top layer first) |

Working examples in `examples/` (HTML + PNG): `findings` (numbered notes, ruled, spiral, desk), `flow` (mind-map, margin ruled, gutter, wood, caps hand), `hub` (dot grid, slate, Nanum hand). The pyramid markup is above. Read the closest example before writing; never copy its content.

**Lay pages out with flex and grid** (`.row`, `.col`, `.cols2`, `display:grid`), not absolute pixel positions. Text size changes with the hand, and absolutely placed blocks then overlap. Absolute positions are only for a staggered mind-map, and only after a render shows no `WARN`.

## Writing rules

- **Title names the subject** and promises the content ("What 400,000 Claude Code sessions show", "What Affleck saw that the labs missed"). It must pass the stranger test (the stranger test: someone who hasn't seen the source reads only the title. Do they know what it's about?). No eyebrow above it.
- Headings are 2–4 words; explanations one or two short lines. Underline the 1–3 words in each point that carry it.
- **Facts only from the source.** Numbers exact. Don't overstate the source (it "saw what the labs missed", not "beat the labs").
- Follow `voice_notes` in **Make it yours** (spelling, case). No emoji.

## Render

Run the script from this Skill's folder (it sits next to this file). It needs Python with Playwright and Pillow; install them first if they're missing (`pip install playwright pillow` then `playwright install chromium`).

```bash
python3 scripts/render.py BODY.html OUT.png \
  --paper ruled|dots|grid|plain [--margin] --binding spiral|gutter|none --surface desk|wood|slate|none \
  --hand indie|shadows|architect|nanum|caps [--head ...] --pen green|blue|red|ink --marker yellow|orange|green|pink \
  [--size portrait|square] --seed N
```

- Output is 2×: portrait 2160×2700 (default), square 2160×2160.
- **Vary the look every time**: paper, binding, surface, hand and pen should not all repeat from the last notebook page. `caps` (tall marker capitals) suits mind-maps; `shadows` and `indie` suit lists; `nanum` and `architect` suit hubs and pyramids.
- It uses rough.js and the drawing script `sketch.js`, both in `assets/` (all the `.hl`, `.ul`, `[data-box]`, `.num`, `.check`, arrows and icons work here).
- Fix every `WARN` (overflow or near the edge) before using the image, then look at it: no text crossing a line or arrow, nothing crowded, highlights on their words.

## Posting

The same image works on LinkedIn, X and Substack Notes. Write a short post that says something the image doesn't, and link the source article underneath it: the LinkedIn first comment, a reply on X, or a "Full article:" line at the end of a Substack Note. Keep links out of the LinkedIn post body.
