# content-engine

A weekly content machine. A scheduled Claude Code routine runs the `content-engine` Skill: trend radar → trend report → posts → infographic and carousel → media on GitHub Pages → Buffer drafts for LinkedIn, X and Substack Notes.

First time? Say "set up my content engine". The `engine-setup` Skill interviews you and fills in `config/engine.yaml`, `design.md`, the radar's settings and your voice guide.

## Layout

- `.claude/skills/` – every Skill the engine uses. `content-engine` is the orchestrator; `engine-setup` configures it.
- `config/engine.yaml` – author, audience, CTAs, which drafts go where, Buffer channel ids, media host.
- `design.md`, `brand/` – brand tokens, fonts, headshot or logo. The graphic Skills read `design.md`.
- `scripts/buffer.py` – lists Buffer channels and creates drafts.
- `scripts/publish_media.py` – copies a run's media into your public media repo so Buffer can fetch it.
- `runs/YYYY-MM-DD-slug/` – one folder per run: radar, report, posts, media, drafts, README.

## Rules

- Everything goes to Buffer as a **draft**. Never publish directly.
- Never invent statistics, quotes or names. Facts come from sources opened during the run.
- Unattended runs never stop to ask. Record decisions in the run README.
- The only thing this repo pushes to the media repo is `{media.path_in_repo}/<run>-<code>/`.
- Never commit API keys. The Buffer key lives in the cloud environment (API credential or `BUFFER_API_KEY`).
- Spelling follows `author.language`. Sentence case. No emoji on graphics.
