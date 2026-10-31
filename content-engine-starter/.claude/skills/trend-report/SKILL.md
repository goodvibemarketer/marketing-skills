---
name: trend-report
description: Turns one trend from the AI Marketing Trend Radar into a short, source-checked brief that posts, infographics and carousels are built from. Use after the radar runs, or when asked to write up a trend for content.
license: Complete terms in LICENSE.txt
---

# Trend report

Takes one trend from a radar run and writes `report.md`: a short brief that every later step builds from. The posts, the infographic and the carousel all read this file and nothing else, so anything not in it doesn't exist downstream.

It is not an article for readers. It is the fact sheet and argument a writer and a designer need, in that order.

## Inputs

- `radar-data.json` from the AI Marketing Trend Radar (the `trends[]` array, `sources`, `chart_of_week`).
- The chosen trend: the one the caller names, otherwise the highest `score`.
- `config/engine.yaml` → `author` (for the angle's point of view).

## Steps

1. **Pick the trend.** Use the caller's choice. Otherwise take the highest `score`, unless another trend has `shelf_life` "Post within 48h" and a score within 10 points of it, in which case take that one.
2. **Check the facts at source.** Open (WebFetch) the 2–5 sources behind the trend's `what`, `stats` and `quotes`. Keep only figures and quotes you can see on the page, with the publication and date. A figure you can't find is dropped, not softened. Note anything the radar got wrong.
3. **Look for one more number if there isn't one.** At most two WebSearch calls for a recent, citable figure that supports the trend. None found is fine: say so, and the graphics will use a framework instead of a chart.
4. **Choose the angle.** Pick one of the trend's three `angles` (hot take, practical, contrarian). Prefer the one the author can argue from their own work (see `config/engine.yaml` → `author.expertise`). Say why in one line.
5. **Write `report.md`** in the shape below. Plain British English, short sentences, no filler. No emoji.

## Output: report.md

```markdown
# {Trend name}

**Controlling idea:** {one sentence: the single claim every asset makes}
**Angle:** {Hot take | Practical | Contrarian}: {the hook line}. Why this angle: {one line}
**Shelf life:** {from radar}  ·  **Post by:** {weekday date}

## What happened
{2–4 sentences. Every fact has a source in brackets: (Publication, date).}

## Why B2B marketers should care
{2–3 sentences about their work, budget, team or pipeline.}

## The numbers
| Figure | What it measures | Source |
| --- | --- | --- |
{Only figures checked at source in step 2. If none: "No checked figures this week. Use a framework, not a chart."}

## The shape of the argument
{The structure a designer can draw: a before/after, a 3–5 step process, a contrast, a framework with named parts, or a ranked list. Name the shape on the first line ("Shape: before/after"), then its parts.}

## What people are saying
{0–2 verbatim quotes with who said them and where. Only quotes seen at source.}

## Author's take
{2–3 sentences in first person: what the author thinks and what they'd tell their audience to do on Monday. Grounded in the facts above, no new claims.}

## Sources
- [{title}]({url}), {publication}, {date}
```

## Rules

- **Never invent.** No statistics, quotes, company names or dates that aren't on a source page you opened. If the trend falls apart when checked, say so at the top and recommend the next trend instead.
- **One idea.** If the trend holds two stories, pick the stronger and leave the other out.
- **Short.** 350–600 words. Downstream skills compress it further.
