# AI News Video — Runbook

A repeatable Claude Code workflow that turns an AI model/product announcement into a short,
voiced YouTube news video in your voice. Speed-first. Two human checkpoints (script approval,
final preview). You upload manually.

## One-time setup

1. **Install the Higgsfield skill** (you already have Higgsfield connected; this adds the CLI skill):
   ```bash
   npx skills add higgsfield-ai/skills
   higgsfield auth login        # if prompted
   ```
2. **Install this skill.** Drop the `ai-news-video/` folder into your project's skills location
   (e.g. `.claude/skills/ai-news-video/`) so Claude Code loads `SKILL.md`.
3. **ElevenLabs.** Get your cloned voice's ID from the ElevenLabs dashboard (Voices → your clone →
   copy voice ID). Then export both, ideally in a `.env` you source:
   ```bash
   export ELEVENLABS_API_KEY="sk_..."
   export ELEVENLABS_VOICE_ID="your_voice_id"
   ```
4. **FFmpeg** must be installed (`ffmpeg -version`). On macOS: `brew install ffmpeg`.
5. Keep your four voice docs in the project (Speaking Style Guide, Kallaway Engine, Tone of Voice,
   Who Is Andy). The skill reads them to keep the script sounding like you.

## Running it (the normal path)

In Claude Code:

> make a news video about https://www.anthropic.com/news/whatever-shipped-today

Claude will:
1. Fetch and read the source, find the marketer angle.
2. Draft `script-teleprompter.txt`, `script-master.md`, `visual-and-metadata.md` into `output/<slug>/`.
3. **Stop and show you the script + fact-check sheet.** ← you verify claims, edit voice, approve.
4. On approval, in parallel: render the voiceover, queue the Higgsfield B-roll. You record the real
   screen captures from the shot list at the same time.
5. Assemble `final.mp4`.
6. **Stop and let you preview.** ← you watch once, confirm the title/description, upload yourself.

## Running the pieces by hand

```bash
# voiceover
scripts/voiceover.sh output/opus-4-8/script-teleprompter.txt output/opus-4-8/voiceover.mp3

# B-roll — copy the commands from visual-and-metadata.md, save results to output/opus-4-8/clips/

# assemble (after dropping your real screen captures into clips/ too, named so they sort in order)
scripts/assemble.sh output/opus-4-8
```

## The two rules that protect the channel

1. **Real product shots are screen captures, not AI.** Higgsfield only makes atmosphere/concept
   B-roll. Never an AI-generated benchmark chart or fake UI.
2. **Nothing renders or publishes without your eyes on it.** The fact-check sheet is there so the
   script check takes 5 minutes, not 20. Use it.

## What's deliberately not here (yet)

- **HeyGen avatar intro** — adds render latency and a failure point that breaks the speed target.
  Add it later as an optional opener for longer evergreen videos, not news.
- **Auto-upload to YouTube** — possible via the API, but you can't unsay a bad take. Manual for now.

## First job is already done
`output/opus-4-8/` contains the finished script, fact-check sheet, B-roll prompts, and metadata for
the Claude Opus 4.8 video. That's your first run — and the worked example for every release after.
