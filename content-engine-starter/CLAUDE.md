# content-engine

A weekly content machine. A scheduled Claude Code routine runs the `content-engine` Skill: trend radar → trend report → posts → infographic (and GIF), carousel and an X image → media on GitHub Pages → Buffer drafts for LinkedIn, X and Substack Notes.

First time? Say "set up my content engine". The `engine-setup` Skill interviews you and fills in `config/engine.yaml`, `design.md`, the radar's settings and your voice guide.

## Layout

- `.claude/skills/` – every Skill the engine uses. `content-engine` is the orchestrator; `engine-setup` configures it; `learn-from-edits` turns your edits in Buffer into voice rules each week; `infographic-animator` makes the GIFs; `sketch-explainer` and `notebook-notes` draw the X image; `substack-notes` turns an article into a week of Notes.
- `config/engine.yaml` – author, audience, CTAs, which drafts go where, Buffer channel ids, media host.
- `design.md`, `brand/` – brand tokens, fonts, headshot or logo. The graphic Skills read `design.md`.
- `scripts/buffer.py` – lists Buffer channels and creates drafts.
- `scripts/publish_media.py` – copies a run's media into your public media repo so Buffer can fetch it.
- `runs/YYYY-MM-DD-slug/` – one folder per run: radar, report, posts, media, drafts, README.
- `runs/notes/YYYY-MM-DD-slug/` – Substack Notes batches from the `substack-notes` Skill (cut from your long-form articles; Buffer drafts without times, you queue them). `runs/notes-log.json` lists every Note sent, so openers and ideas don't repeat.

## Rules

- Everything goes to Buffer as a **draft**. Never publish directly.
- Never invent statistics, quotes or names. Facts come from sources opened during the run.
- Unattended runs never stop to ask. Record decisions in the run README.
- The only thing this repo pushes to the media repo is `{media.path_in_repo}/<run>-<code>/`.
- Never commit API keys. The Buffer key lives in the cloud environment (API credential or `BUFFER_API_KEY`).
- Spelling follows `author.language`. Sentence case. No emoji on graphics.
- When the owner corrects a draft, use `engine-setup` → "Learn from my edits" to turn the fix into a rule in the voice guide.
