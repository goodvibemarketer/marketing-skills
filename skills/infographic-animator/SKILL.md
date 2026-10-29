---
name: infographic-animator
description: Turns a finished 4:5 infographic (1080×1350 layout) into an animated GIF for LinkedIn, X or Substack. Build mode: the graphic builds itself in reading order (highlighter wipes in, numbers count up, line art draws itself, sections fade in), then holds. Loop mode: the finished graphic stays whole and its parts come alive in a seamless loop (gears turn, a conveyor runs, a character talks, looks away or sleeps). Use when asked to "animate the infographic", "make a GIF of this graphic", "turn my infographic into a GIF" or "make the characters move".
---

# Infographic animator

Takes an infographic that already exists and makes it move. The motion is code: the infographic's own HTML is loaded in Chromium, a timeline of effects is applied, the page is stepped frame by frame, and the frames are written to a looping GIF. Nothing is redesigned. The last frame of the GIF is the static infographic, pixel for pixel.

The point of the motion is the first two seconds in the feed: the graphic assembles in the order you want it read, so the eye follows the argument. It is not decoration. If an effect doesn't help the reading order, leave it out.

## Works with the infographic builder

This is an add-on to the free LinkedIn infographic builder Skill (goodvibemarketer.com/skills). Make the infographic with that Skill first, then animate it with this one in the same chat: the builder leaves the HTML this Skill reads best. It also works on any other 1080×1350 infographic, from just the PNG (see Inputs).

## Make it yours (edit this block once)

Fill this in once after installing. Leave a line blank and Claude uses the default.

```yaml
default_mode:     # build (the graphic assembles itself) | loop (the finished graphic comes alive); default build
hold_seconds:     # how long the finished graphic holds before the GIF loops; default 3.5
substack_cut:     # yes | no: also make the lighter Substack Notes version; default yes
channels:         # where your GIFs go, e.g. LinkedIn and Substack Notes
```

Read this block before writing the timeline: use `default_mode` unless the user asks for the other, put `hold_seconds` in `motion.json` as `hold`, and skip the Substack cut only when `substack_cut` is `no`.

## Inputs

1. **The infographic's HTML** (best). The free infographic builder Skill saves it next to the PNG (`infographic.html` beside `infographic.png`). If you have several versions of the graphic (say, one CTA for LinkedIn and one for a newsletter), make one GIF per version.
2. **Only a PNG** (fallback, 1080×1350 or its 2× export at 2160×2700; give band positions in 1080×1350 px). Use PNG mode below: the image is cut into horizontal bands that fade or wipe in. Less lively (no counting, no line drawing), but it works on any 1080×1350 graphic.

## Steps

### 1. Read the graphic and write the reading order

Open the HTML (and look at the PNG). List the blocks in the order a reader should take them in, top to bottom, and note the CSS selector for each: the headline highlighter, the hero number or chart, the hero illustration, each section, the CTA card. Use selectors that already exist in the HTML; don't edit the infographic to add hooks unless a block has no selector at all.

### 2. Write `motion.json`

One timeline in seconds. Each step names a selector, an effect, a start time (`at`) and a duration (`dur`). `stagger` applies the effect to each matched element in turn.

```json
{"hold": 3.5,
 "steps": [
  {"sel": "h1 .hl-mark", "fx": "wipe", "at": 0.2, "dur": 0.6},
  {"sel": ".big", "fx": "count", "at": 0.6, "dur": 1.2},
  {"sel": "svg.hero", "fx": "draw", "at": 1.0, "dur": 0.9, "stagger": 0.05},
  {"sel": ".sites .ic svg", "fx": "pop", "at": 2.8, "dur": 0.3, "stagger": 0.08},
  {"sel": ".st", "fx": "fade", "at": 4.2, "dur": 0.4, "stagger": 0.25},
  {"sel": ".cta", "fx": "fade", "at": 5.1, "dur": 0.4}
 ]}
```

| Effect | Does | Use it on |
| --- | --- | --- |
| `wipe` | Reveals left to right | The headline highlighter, bars in a bar chart, a timeline line |
| `count` | The first number in the element counts up from 0 to its real value | The hero number. Only on numbers that are on the static graphic |
| `draw` | Every SVG stroke draws itself; dashed strokes and SVG text fade in after | Line-art illustrations, diagrams, line charts |
| `pop` | Scales up from 60% with a fade | Icon arrays, waffle squares, step markers |
| `fade` | Fades in with a 16 px rise | Text blocks, cards, the CTA |

Rules for the timeline:
- **Frame 0 must read on its own.** Never animate the headline text or the sign-off strip: they are visible from the first frame, so a feed that shows only the first frame (or a viewer who scrolls fast) still sees what it's about. Animate the highlighter behind the headline, not the words.
- **Reading order, one thing at a time.** Start the next block as the previous one is finishing (overlap by ~0.2s). No two unrelated blocks start together.
- **Build in 4–6 seconds, hold 3–4 seconds.** Longer builds lose people; a short hold doesn't give them time to read the finished graphic. The CTA comes in last.
- **Calm motion.** Durations 0.3–1.2s. No bouncing, spinning, shaking or flashing. Stagger icon arrays at 0.05–0.1s per item.
- **Numbers stay true.** `count` ends exactly on the number printed on the graphic. Don't animate a number up to a value the graphic doesn't show.

### 3. Render

```bash
python3 <this skill's folder>/scripts/animate.py infographic.html motion.json infographic.gif \
  --frames-dir gif-frames
```

Options: `--fps` (default 20; frame delays stay exact at 20, 25 or 10), `--max-mb` (default 4.8). The script uses Playwright's own Chromium (or a preinstalled one at `/opt/pw-browsers/chromium` in Claude's cloud environment). It prints the frame count, timing and file size, and if the GIF is over `--max-mb` it re-encodes with fewer colours, then at a smaller size (864 or 756 px wide). `--substack OUT.gif` also writes the lighter Substack cut from the same frames (see **Substack version**).

**PNG mode.** Pass the PNG instead of the HTML and add `bands` (pixel rows, top and bottom) to `motion.json`. The bands become `.band-1`, `.band-2`… for the steps. Leave the headline and the sign-off strip outside every band so they show from frame 0.

```json
{"hold": 3.5, "bands": [[240, 620], [620, 790], [790, 990], [990, 1190]],
 "steps": [{"sel": ".band-1", "fx": "fade", "at": 0.3, "dur": 0.6},
           {"sel": ".band-2", "fx": "wipe", "at": 1.1, "dur": 0.7}]}
```

### 4. Review and fix (at least once, usually two or three rounds)

Look at frames from across the timeline before calling it done. Make a contact sheet of about 8 frames (first, a few in the build, the last) from `--frames-dir`, and check:
- Frame 0 shows the headline and the sign-off strip, and nothing half-drawn.
- Each block appears in the intended reading order, and nothing pops in out of turn.
- Line art draws cleanly (no stray strokes, no fills appearing before their outlines).
- The counting number ends on the exact printed value.
- The last frame matches the static PNG: no element left hidden, faded or clipped.
- Size ≤ 4.8 MB (or the `--max-mb` you set) and ≤ 240 frames; dimensions 1080×1350 (or 864×1080 if it had to shrink, which you should mention). Frames are captured at 2× and scaled down for smoother text; the GIF itself stays 1080 wide, because a 2× GIF would be about four times the file size.

Fix the timeline and re-render. Delete the frames folder when done.

## Loop mode: make the parts busy instead of revealing the picture

Build mode spends the motion on assembling the graphic. Loop mode does the opposite: **frame 0 is the whole finished graphic**, and the GIF is one seamless loop in which the parts of the picture work: gears turn, pages roll along a belt, a speech bubble cycles through words, a plan fills itself in, a character looks away or falls asleep. The graphic feels alive, and someone who scrolls past on the first frame still sees all of it.

Use loop mode when the graphic has characters or machines that can *do* their job on screen, especially when the motion can act out the idea (in the three-levels example the loop performs the laptop test: the lids close, Level I stops, Level II keeps building while its character looks away, Level III keeps shipping while its character sleeps). Use build mode for charts, numbers and text-led layouts.

### 1. Make the moving parts addressable

In the infographic's HTML, give every part that moves its own id or class, and keep each one in a `<g>` with **no `transform` attribute of its own** (put the position on a parent `<g>`): the effect writes its own transform, and the script warns when it would replace one. Draw each part in its resting pose. For a part that swaps between two looks (an open and a closed laptop, open and closed eyes), draw both and let two `show` effects swap them.

### 2. Write the loop

```json
{"mode": "loop", "period": 7, "fps": 12,
 "loops": [
  {"sel": ".lap-open",   "fx": "show",   "from": 0.93, "to": 0.30, "fade": 0.01},
  {"sel": ".lap-closed", "fx": "show",   "from": 0.30, "to": 0.93, "fade": 0.01},
  {"sel": "#word",       "fx": "cycle",  "words": ["ask", "refine", "copy", "paste"], "from": 0, "to": 0.30},
  {"sel": ".pane",       "fx": "build",  "at": 0.12, "step": 0.15, "until": 0.93},
  {"sel": "#head",       "fx": "flip",   "from": 0.33, "to": 0.90},
  {"sel": "#gear",       "fx": "spin",   "turns": 1},
  {"sel": ".card",       "fx": "travel", "path": [[0, 0, 0, 0, 0], [0.1, 0, 0, 0, 1], [0.7, 58, 0, 0, 1], [1, 64, 168, 50, 0]]}
 ]}
```

Times are fractions of the loop (0 to 1). A window whose `from` is bigger than its `to` wraps round the end of the loop.

| Effect | Does | Settings |
| --- | --- | --- |
| `spin` | Turns about its own centre | `turns` (whole number; negative is anticlockwise) |
| `bob` | Moves gently up and down (or sideways) | `amp` px, `cycles` per loop, `axis` |
| `blink` | Flickers | `cycles`, `low` opacity |
| `cycle` | Swaps its text through a list | `words`, optional `from`/`to` window and `rest` text outside it |
| `build` | Matched parts appear one after another, then clear | `at`, `step`, `fade`, `until` |
| `show` | Visible only inside a window | `from`, `to`, `fade` |
| `flip` | Mirrors left to right inside a window (a head turning away) | `from`, `to` |
| `travel` | Moves along keyframes `[u, dx, dy, rotate, opacity, scale]` from where it's drawn. Several matched parts are spaced evenly round the loop, like items on a conveyor | `path`, `spread` (false to move them together) |

Every effect also takes `offset` to shift it in the loop. Effects on the same part combine.

Rules for loops:
- **Seamless.** Whole turns per loop for anything that spins, whole cycles for bobs and blinks, and every `build`/`show` back to its frame-0 state by the end. The script never holds the last frame.
- **One story per loop.** Every moving part should say something about the idea. Busy for its own sake is noise.
- **Calm.** 6–8 second loops, 12–15 fps. Nothing flashes faster than about 3 times a second.
- **Words stay still.** Headline, labels and the CTA never move, so the graphic reads on any frame.

### 3. Render, with the still

```bash
python3 <this skill's folder>/scripts/animate.py infographic.html loop.json infographic.gif --still 5.7 infographic.png \
  --substack infographic-substack.gif
```

`--still T` saves the frame at T seconds as the 2× PNG (2160×2700), so the static post and the GIF are the same picture. Pick the moment that tells the story best. Loop GIFs change in more places per frame than build GIFs, so they're bigger: keep the moving parts few, use 12 fps, and check the size (the script drops colours, then scale, to get under `--max-mb`). A loop GIF nearly always needs the Substack cut. Review a contact sheet of 8 frames across the loop as in build mode, and check that the first and last frames match.

## Substack version (always make one)

Substack Notes reject GIFs over about 2.5 MB, and a GIF made for LinkedIn (up to 4.8 MB) is often bigger than that, loop GIFs especially. So every GIF that might go on Substack gets a lighter cut:

- **Same graphic for both** (a one-off GIF): add `--substack <name>-substack.gif` to the render. It encodes a second GIF from the same frames, under 2.4 MB: fewer colours first, then a smaller size (864 or 756 px wide) if it has to. Nothing is rendered twice.
- **Different graphic for Substack** (a different CTA card, as in the content engine): render the Substack HTML on its own with `--max-mb 2.4`.

Check the Substack GIF the way you check the main one (first frame, last frame, the headshot in colour), and say in your note if it had to shrink.

## Output

- `<name>.gif` next to the PNG and HTML, and `<name>-substack.gif` (≤ 2.4 MB) for Substack Notes.
- `<name>.motion.json` next to them too, so the animation can be re-rendered after a design fix.
- A one-line note on the timeline (what builds in which order), the frame count, duration and file size.

## Setup (once)

Needs Python 3 with Playwright and Pillow, and a Chromium for Playwright:

```bash
pip install playwright pillow
playwright install chromium
```

Claude runs these for you if they're missing. In Claude's cloud environment Chromium is usually already installed; don't download another one if `/opt/pw-browsers/chromium` exists.

## Limits worth knowing

- GIFs carry 256 colours, shared by every frame. The script gives photos (any `<img>`: the headshot, a logo) extra weight when it picks them, so a small photo keeps its colour instead of turning grey next to large flat areas. Check the headshot is in colour on the first and last frames; it may show slight banding.
- Substack Notes reject GIFs over about 2.5 MB (hence 2.4 MB for the Substack cut).
- LinkedIn plays GIFs in image posts. The figures most often quoted for LinkedIn GIFs are 5 MB and 250–300 frames, but they come from ad specs and third-party guides rather than a LinkedIn page for organic posts, hence the 4.8 MB and 240-frame ceilings here.
- Keep the static PNG as well: carousels, thumbnails and anything that won't play a GIF still use it.
