---
name: substack-notes
description: Turns the owner's long-form articles (and the weekly trend report) into a batch of short, varied Substack Notes (takeaways, quotes, stats, "aha" moments, questions, story beats) and saves them to Buffer as drafts for the Substack queue. Use when asked to "repurpose this article into Notes", "make this week's Notes", or after a new long-form article is published.
---

# Substack Notes

Posting Notes often (`config/engine.yaml` → `notes.per_week`, e.g. 21 for three a day) grows a newsletter. Most of them can come from the owner's own long-form articles: one article holds a dozen Notes if you cut it into single ideas. This Skill does the cutting.

Every Note goes to Buffer as a **draft with no time set**. The owner sets daily posting slots on the Substack queue in Buffer, and each draft they add to the queue takes the next free slot. So the Skill never sets times, and never schedules or publishes anything itself.

## Inputs

- **A long-form article** (URL or text). Fetch it, strip the page furniture, and keep the body. It is the only source of facts for Notes cut from it.
- Optionally **this week's `report.md`** from the content engine, for 2–4 Notes on the week's trend.
- `runs/notes-log.json`: every Note already sent (first line, type, source). Read it first.

## How many

- From one ~1,000-word article: **10–14 Notes**. Don't pad. If the article only holds 9 good single ideas, make 9.
- From a trend report: 2–4.
- A week needs `notes.per_week`. If this batch plus anything already queued is short of that, say how many are missing in the README rather than stretching the source.

## The mix (no two Notes alike)

Cut the article into single ideas, then give each one a different shape. In a batch of 12, use at least 7 of these types and no more than 3 of any one:

| Type | What it is |
| --- | --- |
| `claim` | The article's controlling idea as one sharp sentence plus one line of support |
| `stat` | One number from the article, who found it, and what it means. Name the source in the text |
| `quote` | One of the owner's own lines from the article, lifted nearly verbatim, standing on its own |
| `story` | One beat of the article's story (a scene, a detail), told in 2–4 sentences |
| `aha` | The non-obvious insight: "X wasn't the edge. Y was." |
| `reframe` | Turns a common fear or assumption around, using the article's evidence |
| `how-to` | One concrete action from the article, small enough to do this week |
| `question` | A real question to readers, rooted in the article, that people can answer from experience |
| `contrarian` | Pushes against the popular view, using the article's evidence |
| `link` | Points back to the full article with a one-line reason to read it; carries the article as a link card |

About **1 in 4 Notes are `link` Notes**, spread out, never two in a row. The rest stand on their own: a Note that only works if you read the article is a bad Note.

## Writing rules

- **Facts only from the source,** numbers exact. A Note may leave a fact out; it may not round, stretch or add one. Third-party numbers keep their source in the text ("Anthropic's study of 400,000 Claude Code sessions…").
- **One idea per Note.** 15–120 words. Most should be under 70; Notes read in a fast feed. Mix lengths across the batch: some one-liners, a few longer ones.
- **Openers vary.** No two Notes in a batch start with the same word, and none starts the same way as a Note in the last two weeks of `runs/notes-log.json`. Never open with "Something I noticed this week", "I noticed", "This week I…", "Here's the thing", "Let's talk about", "In today's world", or a rhetorical "Ever wondered…?".
- **Write like the owner:** read `.claude/skills/social-posts/references/voice.md` and `samples.md` first and follow them (spelling, openers, length, emoji, everything), including **Learned from edits**, which wins over other rules here. If the voice guide still says `STATUS: template`, stop and say: "Set up your voice first: say 'set up my content engine' (or 'update my voice guide')."
- **No CTA lines.** No "Subscribe free…", no free-Skills offer, no "More every week at…". Notes show their own subscribe button. No hashtags, no emoji.
- **Pass every Note through the no-ai-slop Skill** (edit mode, keep the voice), then re-check lengths and openers. The voice guide wins: keep what `voice/voice.md` lists under "Keep, even if it looks like AI". Never invent the owner's experiences or past beliefs.

## Images

Mix image Notes in with the text ones so the feed doesn't look the same three times a day:

- **3–4 Notes per batch carry an image**, alternating between a sketch explainer (`sketch-explainer`) and a notebook page (`notebook-notes`): pick the ideas in the source that have a shape (steps, a contrast, a 2×2, a formula) and draw each as a different layout. Square or portrait. The Note's text then says something the image doesn't, rather than repeating it.
- `link` Notes stay text plus link card (Buffer can't attach both). Never put an image Note next to another image Note.
- Save sketches to `runs/notes/<batch>/media/`, host them with `python3 scripts/publish_media.py runs/notes/<batch>` (it writes `media-urls.json`), and use `"asset": {"type": "image", "url": ...}` for those Notes.
- The weekly content engine's own Substack Note already carries the infographic or its GIF.

## Output

Folder: `runs/notes/YYYY-MM-DD-<article-slug>/`

- `source.md`: the article text as fetched, with its URL and title.
- `notes.json`: `[{"n": 1, "type": "stat", "text": "...", "link": null | {"url": ..., "title": ..., "description": ...}, "image": null | "media/sketch-<n>.png"}]`
- `notes.md`: the batch for reading, each Note under `## n. type`.
- `drafts.json`: one entry per Note: `{"channel": "substack", "post": "note-<n>", "text": ..., "asset": null}`. For `link` Notes, `"asset": {"type": "link", "url": ..., "title": ..., "description": ...}`.
- `README.md`: source, count, the mix by type, anything left out and why, and the Buffer ids.

Then:
1. `python3 scripts/buffer.py drafts runs/notes/<batch>/drafts.json --dry-run`
2. `python3 scripts/buffer.py drafts runs/notes/<batch>/drafts.json` (re-running skips Notes already sent)
3. Append each Note to `runs/notes-log.json`: `{"date", "batch", "n", "type", "first_line", "buffer_id"}`.
4. Commit `runs/notes/<batch>/` and the log to `main` and push.

## Self-check before sending

- Every number and name traces to the source text?
- At least 7 types, none more than 3 times, link Notes about 1 in 4 and never adjacent?
- 3–4 image Notes (sketch and notebook mixed), different layouts, none next to each other, each image checked? Image Notes end with "Full article: {url}".
- No two openers alike, none of the banned openers, no CTA line, no hashtags or emoji?
- Each Note makes sense to someone who hasn't read the article?
