---
name: content-engine
description: Runs the weekly content machine end to end: trend radar, trend report, social posts, infographic and carousel for each channel, hosts the media, and saves everything to Buffer as drafts. Use when asked to "run the content engine", "do this week's content", or by the weekly scheduled task.
license: Complete terms in LICENSE.txt
---

# Content engine

One run turns this week's trends in your field into a ready-to-approve content pack: posts for LinkedIn, X and Substack Notes, with an infographic and a carousel, sitting in Buffer as **drafts**. Nothing is published. You approve in Buffer.

Usually this runs unattended on a schedule. **Never stop to ask a question.** Where a choice is needed, make the sensible one, write it down in the run's `README.md`, and carry on. If a step fails, finish what you can, record the failure, and still commit (step 9).

Settings live in `config/engine.yaml`. Brand lives in `design.md` and `brand/`. If `config/engine.yaml` still has a blank `author.name`, or `design.md` still contains `TODO`, stop and say: "Run setup first: say 'set up my content engine'." (In an unattended run, write that in the README, commit and finish.)

## Step 0: Set up the run

1. `TODAY=$(date -u +%F)`. Create `runs/$TODAY-draft/` (renamed in step 2 once the trend is known).
2. Check tools: `python3 -c "import playwright, yaml, PIL"`. Install what's missing with `pip install --break-system-packages playwright pyyaml pillow`. Don't run `playwright install` if Chromium is preinstalled (`/opt/pw-browsers`).
3. Fonts: load the fonts named in `design.md`. Files in `brand/fonts/` load with `@font-face`; for a Google font missing from the machine, `npm i --prefix /tmp/fonts @fontsource/<font-name>` and load its woff2 files.
4. Check Buffer access: `python3 scripts/buffer.py orgs`. If it fails, run everything else and skip step 8, recording why.

## Step 0b: Learn from last week's edits

Run the **learn-from-edits** Skill (unattended mode): `python3 scripts/buffer.py edits --all`, then turn what the owner changed in earlier drafts into [proposed] rules in the voice guide, before this week's posts are written. If Buffer isn't connected yet, skip this and say so in the README.

## Step 1: Trend radar

Run the **ai-marketing-trend-radar** Skill in radar mode with its saved Settings, with these overrides for unattended runs:
- Skip the Setup offer.
- Skip publishing an artifact and sending files. Save the report as `radar.md` and the data as `radar-data.json` in the run folder. Building the PDF is optional; skip it if time or usage is tight.

## Step 2: Trend report

Run the **trend-report** Skill on `radar-data.json`. It writes `report.md`. Rename the run folder to `runs/$TODAY-<trend-slug>/` (slug: 3–6 lowercase words, hyphenated).

If the report says the trend fell apart on checking, run trend-report again on the next trend. If two trends fail, stop the content steps, write the README, commit, and finish.

## Step 3: Posts

Run the **social-posts** Skill on `report.md`. It writes `posts.json` and `posts.md`.

## Step 4: Graphics

All graphics follow `design.md` (it overrides any footer or CTA rules inside the graphic Skills) and use `report.md` as their only source. Save into `media/`:

| File | Made with | CTA (from `design.md` → Channel CTAs, wording from `config/engine.yaml`) |
| --- | --- | --- |
| `infographic-linkedin.png` | **linkedin-infographic-builder** | `linkedin`: follow/save card from `design.md` |
| `infographic-substack.png` | the same design, re-rendered | `substack`: subscribe card. Change only the CTA block, nothing else |
| `carousel.pdf` | **linkedin-carousel-builder** (6–8 slides) | Last slide: `linkedin` follow/save slide (dark) |
| `carousel-cover.png` | slide 1 of the carousel, 1080×1350 | (Buffer's document thumbnail) |

Build the infographic once as HTML with the CTA as a swappable block, and render it twice. Keep the HTML in `work/`.

**Variety.** Read `runs/graphics-log.json` (create it if missing). Pick the infographic's layout archetype, main chart type and hero illustration with the infographic Skill's Variety, Hero illustration and Chart chooser rules: not the same archetype as either of the last two runs, not the same main chart type as the last run. Never copy a previous run's `work/*.html` as a starting point. When done, append `{"run": ..., "archetype": ..., "chart": ..., "hero": ...}` to the log. Same for the carousel: vary chart types across slides, and give the cover a line-art illustration.

**Headlines first.** Before any layout, write three headline options for the infographic and for the carousel cover, following `design.md` → Headlines. Pick the one that passes the stranger test and save all of them in `work/headlines.md`. Then write every carousel slide headline so each one names its subject.

**Check before moving on.** Look at every PNG and at the carousel pages. First, the two hard fails: anything above a headline (eyebrow, kicker, date line or label) on any graphic or slide, and any headline that doesn't name its subject in plain words. Fix those before anything else. Each must be exactly 1080×1350. Fix overflow, cut-off text, a headline word orphaned on its own line, a missing hero illustration, a layout that repeats the last run's, a chart type that doesn't suit its data, a highlight that misses its words, or colours that don't follow `design.md` (highlighter `--highlight`; highlighted chart series and big numbers `--accent`). Every number on a graphic must appear in `report.md`.

## Step 5: Host the media

Buffer needs a public URL for every image and PDF. They go to your media repo (`config/engine.yaml` → `media.repo`), a public GitHub repo with GitHub Pages switched on.

If `../<media repo name>` isn't cloned next to this repo, clone it: `git clone https://github.com/<media.repo> ../<media repo name>`. (In a routine, add the media repo to the routine's repositories so it is already there.)

Then run `python3 scripts/publish_media.py runs/<run>` (add `--media-repo <path>` if the media repo was cloned somewhere other than next to this repo). It commits only `<path_in_repo>/<run>-<code>/` to the media repo's main branch, pushes, waits until GitHub Pages serves the files, and writes `media-urls.json`. If the files aren't live within the wait, record it, skip step 8, and finish.

## Step 6: Build drafts.json

For each channel and slot in `config/engine.yaml` → `drafts`, add one entry:

- `text`: `posts.json[<post>].text`
- `asset`:
  - `infographic` → `{"type": "image", "url": <infographic-linkedin.png URL for linkedin, infographic-substack.png URL for x and substack>}`
  - `carousel` → `{"type": "document", "url": <carousel.pdf URL>, "thumbnail_url": <carousel-cover.png URL>, "title": posts.json.linkedin_carousel.document_title}`
  - `none` → `null`

Write it to `runs/<run>/drafts.json`.

## Step 7: Dry run

`python3 scripts/buffer.py drafts runs/<run>/drafts.json --dry-run`. Fix anything it rejects.

## Step 8: Send to Buffer

`python3 scripts/buffer.py drafts runs/<run>/drafts.json`. Every post is saved as a draft. Never change `saveToDraft` and never publish directly. If a channel id is missing from the config, record it and skip that channel.

## Step 9: Write up and commit

`runs/<run>/README.md`:

```markdown
# {Trend name}, week of {TODAY}

**Status:** {Drafts in Buffer | Files only: <reason>}
**Controlling idea:** {from report.md}
**Why this trend:** {score, shelf life, angle}

## In Buffer
| Channel | Post | Asset | Buffer id |

## Check before approving
- {each figure on the graphics, with its source}
- {anything provisional, e.g. voice guide still waiting for samples}

## Voice rules learned from your edits
- {each rule added in Step 0b, with its before → after; or "None new". Say "confirm the edit rules" or "drop the rule about …"}

## Teach it your voice
Edit drafts in Buffer as you normally would: next week's run compares them with what it wrote and learns the rules. You can also tell Claude directly ("learn from my edits").

## Decisions made
- {every choice made without asking}

## Problems
- {failures, fallbacks, skipped steps; "None" if clean}
```

Delete `work/` scratch files over 5 MB. Then commit everything in `runs/<run>/` to this repo's `main` with the message `run: {TODAY} {trend name}` and push.

## Step 10: Report back

If a `SendUserMessage` or notification tool is available, send the owner a short summary: the trend, what's in Buffer, anything to check, and the link to the run folder on GitHub. Otherwise end with that summary as the final message.
