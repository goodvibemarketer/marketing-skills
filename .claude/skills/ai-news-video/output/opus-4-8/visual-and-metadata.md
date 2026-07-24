# Opus 4.8 Video — Visuals, Fact-Check & Metadata

## The accuracy rule (read first)

This channel's whole promise is accuracy. So the split is hard:

- **REAL screen captures** (you record these): anything showing the actual product — the
  benchmark comparison table, the effort control UI, the pricing section, the announcement page.
  Never let an AI model generate a fake chart or a fake UI. That's the visual version of the
  fabrication problem, and it's the fastest way to lose trust.
- **Higgsfield B-roll** (generate these): atmosphere and concept only. No baked-in text, no fake
  product. Abstract, brand-adjacent motion you cut to between the real captures.

---

## Shot list — REAL captures (record yourself)

1. Announcement page scrolling (anthropic.com/news/claude-opus-4-8).
2. The benchmark comparison table from the announcement.
3. The effort control sitting next to the model selector on claude.ai. Show yourself turning it.
4. The pricing section.
5. (Optional) fast mode toggle / where the speed setting lives.

---

## Higgsfield B-roll prompts (CLI-ready)

Default video model is `seedance_2_0`. 16:9 for YouTube. Keep them abstract — these are cutaways,
not the star. Drop the `.mp4` results into `output/opus-4-8/clips/` for assembly.

```bash
# 1. Cold-open sting (~4s) — fast, abstract, premium, sets energy
higgsfield generate create seedance_2_0 \
  --prompt "Abstract dark editorial title sequence, deep charcoal background, a single warm amber light sweeping across a clean geometric form, fast confident camera move, premium tech documentary mood, no text" \
  --duration 4 --aspect_ratio 16:9 --resolution 720p --wait

# 2. The dial concept (~4s) — for the effort-control section
higgsfield generate create seedance_2_0 \
  --prompt "A single minimalist physical dial on a clean dark surface, a hand turns it smoothly, soft depth of field, warm rim light, tactile and deliberate, macro, no text, no UI" \
  --duration 4 --aspect_ratio 16:9 --resolution 720p --wait

# 3. Honesty / steadying into focus (~4s) — for the banger section
higgsfield generate create seedance_2_0 \
  --prompt "An out-of-focus scene resolving smoothly into sharp clarity, clean light, a sense of something steadying and becoming trustworthy, calm confident motion, abstract, no text" \
  --duration 4 --aspect_ratio 16:9 --resolution 720p --wait

# 4. Parallel agents (~4s) — for the dynamic workflows aside
higgsfield generate create seedance_2_0 \
  --prompt "Many small glowing nodes working in parallel across a dark grid, organised and purposeful, lines connecting and resolving, top-down, premium abstract data-motion, no text" \
  --duration 4 --aspect_ratio 16:9 --resolution 720p --wait

# 5. Outro sting (~3s) — calm landing
higgsfield generate create seedance_2_0 \
  --prompt "Warm amber light settling to rest on a clean dark surface, slow exhale of motion, premium minimal end-card mood, no text" \
  --duration 3 --aspect_ratio 16:9 --resolution 720p --wait
```

---

## Fact-check sheet (verify before voiceover renders)

Every specific claim in the script, mapped to the source. Scan this, don't re-read the article.

| Claim in script | Source line | Status |
|---|---|---|
| Opus 4.8 shipped, builds on 4.7, better across benchmarks | "We're upgrading Claude Opus to a new version… builds on Opus 4.7 with improvements across benchmarks" | ✅ |
| Effort setting next to the model picker, on every plan | "A new control alongside the model selector… available on all plans" | ✅ |
| Down = faster + slower limit burn; up = thinks more deeply | "higher effort settings, Claude will think more… lower effort settings… respond faster and use up a user's rate limits more slowly" | ✅ |
| ~4× less likely to let a flaw slip through unflagged | "around four times less likely than its predecessor to allow **flaws in code** it has written to pass unremarked" | ⚠️ **The 4× figure is specifically about CODE flaws.** Script keeps it general. Either tighten the line to "in code it writes" or keep general but know the stat's scope. Your call. |
| More likely to flag uncertainty, less likely to make things up | "more likely to flag uncertainties about its work and less likely to make unsupported claims" | ✅ |
| Same price, same input/output cost | "$5 per million input tokens and $25 per million output tokens… unchanged from Opus 4.7" | ✅ |
| Fast mode now 3× cheaper than before | "fast mode for Opus 4.8… is now three times cheaper than it was for previous models" | ✅ (fast mode also runs at 2.5× speed) |
| Dynamic workflows lets Claude Code take on bigger jobs | "Dynamic workflows… run hundreds of parallel subagents… codebase-scale migrations" | ⚠️ Research preview, and **Enterprise/Team/Max only** — not all plans. Script doesn't claim otherwise, just don't add "on every plan" here. |

---

## YouTube metadata

**Title (pick one — "Claude Opus 4.8" stays near the front for search):**
1. Claude Opus 4.8 is here — and the real upgrade isn't coding
2. Claude Opus 4.8: what actually matters for marketers (not the benchmarks)
3. Claude Opus 4.8: the upgrade most people will miss

**Description:**
```
Anthropic just shipped Claude Opus 4.8. Most coverage leads with the benchmarks. I think the real story is something else: a model that's more honest, an effort dial you can actually use, and the same price as before.

Here's what actually changes for marketers and solo creators.

00:00 The boring bit (benchmarks)
00:20 1. Effort control — the dial you should use
00:55 2. It's more honest (the real story)
01:40 3. Same price, better model
02:05 One for the builders: dynamic workflows
02:20 The bottom line

Source: https://www.anthropic.com/news/claude-opus-4-8

I break down what new AI releases mean for marketers every week. Newsletter: [LINK]
```
*(Adjust timestamps to the final cut.)*

**Tags:** Claude Opus 4.8, Anthropic, Claude AI, AI for marketers, AI news, Claude effort control, AI model update, AI for solo creators, GoodVibeMarketer, Claude Code
