# Weekly routine

Create at claude.ai/code/routines → **New routine**.

- **Name:** Weekly content engine
- **Repositories:** this repo **and** your media repo
- **Environment:** the one with your Buffer API credential (see Part 5)
- **Trigger:** Schedule → Weekly → Monday, 06:53 (a few minutes off the hour starts on time)
- **Connectors:** remove all of them; the engine doesn't need any
- **Instructions:** paste everything between the lines

---

Run my weekly content engine, unattended.

1. In the content-engine repo, read CLAUDE.md, then follow .claude/skills/content-engine/SKILL.md from step 0 to step 10 exactly.
2. The media repo is cloned in this session too. If it isn't in the folder next to content-engine, find it and pass its path to scripts/publish_media.py with --media-repo <path>.

Rules: never stop to ask a question; record every decision and failure in the run README. Everything goes to Buffer as drafts only, never published. Never invent figures. The only thing you may push to the media repo is the run's media folder, via scripts/publish_media.py. Commit the run folder to this repo's main branch and push it, even if some steps failed. Finish with a short summary: the trend, what's in Buffer, what to check before approving, and the GitHub link to the run folder.

---
