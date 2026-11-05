---
name: performance-review
description: Reads how the owner's published posts actually performed in Buffer (impressions, engagement, Substack subscribers), joins it to what the engine knows about each post (graphic type, length, topic, Note type, day and time), and writes a performance report. Only patterns backed by enough data are proposed as rules, and a rule only applies once the owner confirms it. Runs as a step of every content engine run, and on request - "how are my posts doing?", "what performs best?", "performance report", "best time to post", "confirm the performance rule".
---

# Performance review

Answers "what works?" from the owner's own numbers, without jumping to conclusions: **a meaningful volume of data comes before any rule.** So this Skill reports every week, but proposes a change only when a pattern is proven, and changes nothing until the owner confirms it.

## 1. Fetch and tag

```bash
python3 scripts/performance.py fetch
python3 scripts/performance.py untagged
```

`fetch` pulls every published post on each channel with its metrics, and joins the engine's own record of it (run, post type, graphic: infographic, infographic GIF, carousel, sketch, notebook page, link card or text only; topic themes from the radar; Note type). Posts the owner wrote outside the engine come through as `source: manual`.

`untagged` lists posts with no topic. Tag each one in `runs/performance/tags.json` (`{"<buffer id>": {"themes": [...], "by": "claude", "tagged_on": "YYYY-MM-DD"}}`), 1–3 tags from this fixed list only:

`claude` · `launch` · `search` · `agents` · `content` · `data` · `teams` · `trust` · `backlash` · `building` (the owner describes something they built or how they build) · `promo` (the post's main job is to promote their newsletter, an offer, a guide or an article)

Tag what the post is mainly about. Never change an existing tag unless the owner asks.

## 2. Report

```bash
python3 scripts/performance.py report
```

It writes `runs/performance/report-YYYY-MM-DD.md` and `findings.json`, per channel, by graphic, length, day, time (UK), topic and Note type. How it judges (thresholds in `config/engine.yaml` → `performance`):

- **Relative performance**, not raw numbers: each post against the median of the same channel's posts within 45 days, so a growing or shrinking audience doesn't look like a format effect.
- **Medians**, so one viral post can't decide anything.
- **Not enough data:** fewer than 5 posts in a group.
- **Early signal:** shown for interest, **never acted on**.
- **Proven:** at least 10 posts in the group and 10 to compare against, at least 40 posts on the channel, a significance test (p < 0.05), and the same result in the first and second half of the period.

Read the report before writing about it. Check anything surprising against the posts themselves (a "proven" topic driven by three near-identical posts is not a pattern; say so).

## 3. Propose rules (proven patterns only)

For each proven pattern not already in `.claude/skills/content-engine/references/performance-rules.md`, write a proposed rule there under **Proposed**, in plain words, with the evidence: "LinkedIn: text-only posts get more impressions than posts with an image (24 posts, 1.31× typical, p=0.003, both halves of the year). [proposed YYYY-MM-DD]". Say what it would change in the engine (e.g. "make one of the two weekly LinkedIn posts text only").

Never propose a rule from an early signal, however striking. Never move a rule to **Confirmed** yourself.

When the owner confirms one ("confirm the performance rule about …"), move it to **Confirmed** with the date. When they reject one, move it to **Rejected** with the date, so it isn't proposed again unless the evidence changes a lot (the group at least doubles in size).

Confirmed rules are what the engine follows: the content-engine and social-posts Skills read the **Confirmed** section. A confirmed rule that later stops being proven (it drops to an early signal for 8 weeks running) goes back to the owner as "still worth keeping?", not silently removed.

## 4. Tell the owner

- **In a weekly run** (unattended): add a short **Performance** section to the run README: posts counted per channel, any newly proven pattern with its proposed rule, and the two or three most interesting early signals, labelled as early signals. Don't ask anything.
- **When the owner asks:** answer from the latest report in plain words, with the numbers and how many posts each is based on. If he asks about something the data can't show yet (best posting time, when the posts all went out at similar times), say so and say what it would take: for timing, a test where the Buffer queue slots rotate for 4–6 weeks so each slot gets enough posts.

## Rules

- Never invent or round numbers. Quote them from the report.
- Never present an early signal as a finding.
- Read-only on Buffer. Commit `runs/performance/` and the rules file with the run.
