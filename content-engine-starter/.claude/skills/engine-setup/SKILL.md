---
name: engine-setup
description: Sets up the content engine for a new owner - their brand, audience, industry, voice, channels, Buffer and media hosting - by interviewing them and filling in config/engine.yaml, design.md, the radar settings and the voice guide. Use when asked to "set up my content engine", "configure the engine", "update my voice guide", "change my brand" or "change my audience".
---

# Engine setup

Turns the starter kit into *your* content engine. You ask the owner a short series of questions, then write their answers into the files every other Skill reads. Interactive: never run this from a routine.

Ask **one topic at a time**, in plain language, offering a sensible default they can accept with "yes". Don't dump all the questions at once. Show what you're about to write before you write it. At the end, commit and push.

## What gets filled in

| File | What goes in it |
| --- | --- |
| `config/engine.yaml` | `author` (name, role, company, LinkedIn URL, newsletter URL, expertise, audience, industry, region, language), CTA lines, channels, Buffer ids, media repo |
| `.claude/skills/ai-marketing-trend-radar/SKILL.md` → Settings block | topic, audience, audience_detail, region, voice, focus, exclude, priority, official_sources, queries, subreddits, trade_press, design_system, setup_done: true |
| `design.md` | every `TODO`: colour tokens, fonts, sign-off strip, Substack/X free offer |
| `brand/` | headshot (`headshot.jpg`) or logo (`logo.svg`/`logo.png`), font files if needed |
| `.claude/skills/social-posts/references/samples.md`, `voice.md` | their best posts, and the voice guide distilled from them |

## The interview

**1. You.** Name as it should appear on graphics, role, company, LinkedIn profile URL, newsletter URL if any, UK or US spelling.

**2. Your audience.** Who the content is for, as specifically as they can say it: role, company type and size, industry, region. Write `author.audience` as one line ("ops leaders at UK logistics firms with 50–500 staff"). This is their ICP; every relevance test and angle uses it.

**3. Your expertise.** What they can talk about from their own work. The trend report picks angles they can actually argue. Two or three lines.

**4. What the radar watches.**
- Topic (default: "AI for business and marketing").
- Focus: the parts of their field they cover. Offer a list built from their answers to 2 and 3; let them cut it.
- Exclude: anything to drop even when it trends (e.g. "paid ads", "crypto", "politics").
- Priority: a vendor or subject they want to be first on (e.g. "Claude and Anthropic releases", "HubSpot updates", "UK employment law changes") and that vendor's official news pages.
Then generate, show and confirm: 10–14 `queries` as people actually write them, 6–10 `subreddits` where their audience and topic meet, 6–10 `trade_press` domains their audience reads. Only include sources you're confident exist.

**5. Your brand.** Ask, in this order of preference:
1. A link to their Claude Design System → read its tokens, fonts and logo/headshot assets.
2. Their website URL → read its CSS colours and fonts with WebFetch.
3. Hex colours and font names typed in chat.
Map what you find to the tokens in `design.md` (`--canvas`, `--ink`, `--highlight`, `--accent` and the rest). Check contrast: `--ink` and `--accent-text` must read clearly on `--canvas` (4.5:1 or better). Ask for a headshot (personal brand) or logo (company page) and save it in `brand/`. For a font that isn't on Google Fonts, ask for the woff2 files.
**Preview:** build one sample infographic with the linkedin-infographic-builder Skill using a made-up headline and no numbers ("Sample: your brand on a graphic"), render it, and show it. Fix what they flag before saving.

**6. Channels and calls to action.**
- Which channels: LinkedIn, X, Substack Notes (remove the others from `drafts`).
- Substack and X lines: what they say at the end of a Note or post, and the three-line free offer on their graphics (what a new subscriber gets). If they have a paid tier, the three-line paid offer for the carousel's last slide.

**7. Your voice.** Ask them to paste 15–20 of their best posts, highest impressions first (LinkedIn → Analytics → Content → export, or copy by hand). Save them to `samples.md` exactly as written. Then distil `voice.md`:
- **What performs**: compare the top five with the bottom five. Length, how they open, where the number goes, whether there's a turn, how they close. Be specific and use their numbers.
- **How you write**: 6–10 bullets, each with a short quote from their own posts as the example.
- Keep the **Rules for drafts** section, adjusting spelling and emoji to what they actually do.
If they don't have posts yet, write the voice guide from 3–5 posts they admire and say in the guide that it's provisional.

**8. Buffer and media.** Check what's done and give the exact next step for what isn't (Part 5 of the guide has every click):
- Media repo: a public GitHub repo (e.g. `content-media`) with GitHub Pages on (Settings → Pages → Deploy from a branch → `main` / root). Fill `media.repo` and `media.base_url` (`https://<user>.github.io/<repo>`).
- Buffer: channels connected in Buffer, API key added to the cloud environment as an API credential for `api.buffer.com`. Then run `python3 scripts/buffer.py orgs` and `python3 scripts/buffer.py channels`, and fill `buffer.organization_id` and `buffer.channels`.

## Finish

1. Run the content-engine Skill's checks: no `TODO` left in `design.md`, `author.name` set, radar `setup_done: true`.
2. `python3 scripts/buffer.py drafts <a tiny test drafts.json> --dry-run` with one text-only LinkedIn entry, to prove the config parses.
3. Commit everything with `setup: <name>'s content engine` and push to `main`.
4. Tell them, in three lines: what's set up, what's still missing (if anything), and the next step: "Run it once by hand: say 'run the content engine'." Then point them to Part 5 of the guide for the weekly routine.
