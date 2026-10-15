# Content engine starter kit

From the AI Marketing Engineer's Guide by Andy Mills (goodvibemarketer.substack.com).

Every Monday a Claude Code routine reads the week's news in your field, picks the trend that matters most to your audience, checks the facts, writes your LinkedIn, X and Substack posts in your voice, designs a branded infographic and carousel, and saves everything in Buffer as drafts. You review, tweak and schedule. Nothing posts without you.

## What's in here

```
.claude/skills/
  engine-setup/                 run once: makes the engine yours
  content-engine/               the weekly run, start to finish
  ai-marketing-trend-radar/     finds this week's trends
  trend-report/                 turns one trend into a fact-checked brief
  social-posts/                 writes the posts in your voice
    references/voice.md         your voice guide (setup writes it)
    references/samples.md       your best posts (you paste them)
  linkedin-infographic-builder/ one 1080x1350 branded infographic
  linkedin-carousel-builder/    a 6-8 slide carousel PDF
  no-ai-slop/                   edits drafts so they don't read as AI
config/engine.yaml              your settings
design.md                       your brand, for the graphics
brand/                          headshot or logo, fonts
scripts/buffer.py               lists Buffer channels, creates drafts
scripts/publish_media.py        puts images online for Buffer
ROUTINE.md                      the prompt for your weekly routine
runs/                           one folder per weekly run
```

## Quick start

1. Make a **private** GitHub repo called `content-engine`, open it in Claude Code at claude.ai/code and say: *"Copy everything in the content-engine-starter folder from https://github.com/goodvibemarketer/marketing-skills into the root of this repo, including the hidden .claude folder, and commit it."* (Part 2 of the guide.)
2. In the same session, say **"set up my content engine"**.
3. Say **"run the content engine"** and check the result.
4. Make the public media repo, connect Buffer, and create the weekly routine with the prompt in `ROUTINE.md` (Part 6).

You need: a Claude Pro or Max plan (routines and cloud sessions; on Team or Enterprise see Part 6's note on API keys), a GitHub account (free), and Buffer with your channels connected.
