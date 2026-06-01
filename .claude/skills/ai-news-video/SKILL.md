---
name: ai-news-video
description: >
  Turn an AI model/product announcement into a short, voiced YouTube news video in Andy's voice.
  Use when Andy says "make a news video about <url>", "Anthropic/OpenAI/Google just shipped X",
  "turn this announcement into a video", or wants to repurpose an Andy's Take blog post into video.
  Orchestrates: fetch source -> draft script (Andy's voice) -> fact-check sheet -> [Andy approves]
  -> ElevenLabs voiceover -> Higgsfield B-roll -> FFmpeg assembly -> [Andy previews] -> YouTube
  metadata. Two human checkpoints. Speed-first: target announcement-to-publish-ready under 2 hours.
allowed-tools: Bash, Read, Write, WebFetch
---

# AI News Video

Produces a short news video (target 2–3 min) from a single source URL, in Andy's voice, fast.
This channel competes on **speed and a sharp marketer angle**, not polish. First-to-publish with a
genuinely useful take wins the search traffic in the first 24 hours after a release.

## Voice & accuracy are non-negotiable

Before drafting anything, read the project's voice docs and apply them:
- **Speaking Style Guide** — how Andy talks (the words, rhythm, "Right.", "I think", "in a nutshell", "cheers").
- **Kallaway Viral Scripting Engine** — structure (hook format, 2-1-3 body order, V-A-V intro, native CTA).
- **Tone of Voice Guide** — the "explain the consequence, not the engineering" reframing rule.
- **Who Is Andy** — context and the family/personal guardrails.

Structure comes from Kallaway. Words come from the Speaking Style Guide. Run the "Does this sound
like Andy?" test before showing him the script.

**Accuracy rule:** This is a news channel built on trust. Every specific claim (numbers, "X times",
prices, "available on all plans") must be traceable to the source. Produce a fact-check sheet
alongside every script. Flag any claim whose scope is narrower than the script implies (e.g. a stat
that's about code specifically, not "everything"). Never let an AI model generate a fake product
screenshot, fake benchmark, or fake UI — real product shots are screen captures Andy records.

## The pipeline

### Stage 1 — Fetch & understand the source
- Fetch the URL (WebFetch, or `scripts/fetch_article.py <url> > output/<slug>/source.txt` for a saved copy).
- For breaking releases, also pull one or two secondary sources (TechCrunch / VentureBeat) to
  cross-check facts, but the primary source is the source of truth.
- Identify the **marketer angle**: what does this change for a marketer or solo creator on Monday
  morning? Most coverage leads with benchmarks/engineering. Andy's job is the reframe. Lead with it.

### Stage 2 — Draft the script
- Pick a Kallaway hook format (Contrarian and Investigator usually fit Andy best).
- Order the body 2-1-3 by impact.
- Write two outputs to `output/<slug>/`:
  - `script-master.md` — 2-column table (visual directions + spoken script).
  - `script-teleprompter.txt` — clean spoken-only, ready for ElevenLabs. ~150 wpm; 350–450 words ≈ 2.5 min.
- Write `visual-and-metadata.md` — Higgsfield prompt list, real-capture shot list, fact-check sheet,
  and YouTube title/description/tags.

### Stage 3 — CHECKPOINT 1 (Andy approves the script)
Show Andy the teleprompter script + the fact-check sheet. He verifies claims, edits voice, approves.
**Do not render voiceover until he approves.** This is the gate that protects the brand.

### Stage 4 — Generate assets (run in parallel)
Kick these off together the moment the script is approved:
- **Voiceover:** `scripts/voiceover.sh output/<slug>/script-teleprompter.txt output/<slug>/voiceover.mp3`
- **B-roll:** run the `higgsfield generate create ...` commands from `visual-and-metadata.md`.
  Save clips to `output/<slug>/clips/`. (Uses the installed `higgsfield-generate` skill / CLI.)
- Remind Andy to record the real screen captures from the shot list in parallel.

### Stage 5 — Assemble
`scripts/assemble.sh output/<slug>` stitches voiceover + clips + captions + intro/outro into
`output/<slug>/final.mp4`. Assembly is the part most likely to need hand-tuning — for v1, Andy may
prefer to assemble in his editor (CapCut/Resolve) while everything else stays automated. That's fine.

### Stage 6 — CHECKPOINT 2 (Andy previews)
Andy watches `final.mp4` once. Confirms title/description/tags from `visual-and-metadata.md`.
Then he uploads manually. **Do not auto-publish news content** — there's no taking back a bad take.

## Repurposing an "Andy's Take" blog post
Same pipeline, simpler: skip Stage 1 monitoring, feed the published article as the source, allow a
longer runtime (5–8 min), no fact-check sheet needed (it's Andy's own thinking). The reframe step
becomes "tighten to the single sharpest argument for video."

## Notes
- Avatar intro (HeyGen) is deliberately out of scope for v1: it adds render latency and a failure
  point that breaks the speed target. Add it later as an optional opener for evergreen videos.
- Keep `output/<slug>/source.txt` and the fact-check sheet after publishing — they're your record
  if a take needs correcting later.
