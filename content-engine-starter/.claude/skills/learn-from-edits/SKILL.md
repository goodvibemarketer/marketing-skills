---
name: learn-from-edits
description: Finds what the owner changed in the engine's drafts before posting them (by comparing each draft with the post in Buffer), works out the general rule behind each change, and adds it to the voice guide so the next drafts don't need the same fix. Runs automatically at the start of every content engine run, and on request - "check my edits", "learn from my edits", "what did I change last week?", or when the owner describes a change in their own words.
---

# Learn from edits

The owner approves every draft in Buffer, and often rewrites part of it first. Each rewrite says something about their voice that the voice guide didn't. This Skill reads those rewrites and turns them into rules in `.claude/skills/social-posts/references/voice.md` → **Learned from edits**, which the social-posts Skill follows.

## 1. Find the edits

```bash
python3 scripts/buffer.py edits --all
```

For every run folder with drafts in Buffer, it compares each draft the engine sent with the post as it is in Buffer now, and writes `edits.json` in that folder. Each post is:

- **edited:** the text (or the LinkedIn first comment, or the X reply) changed. `edits` holds the draft, the posted version and the word-level changes.
- **unchanged:** posted as drafted. Worth noting too: whatever it did, keep doing.
- **deleted:** the draft was removed from Buffer. A weak signal: the owner may have rejected it, or replaced it with another version. Never make a rule from a deletion alone.
- **pending:** still a draft or scheduled. It may change again, so don't learn from it yet.

Skip edits already learned: `runs/edits-log.json` lists every Buffer id taken into account, with the date. When the owner describes a change in their own words instead, go straight to step 2 with what they said.

## 2. Work out the rules

Read every edited post: the draft and the posted version side by side, not just the word changes. For each one, ask what kind of change it is, and look for the same change across posts. Kinds of change:

- **Opening:** a new first line, or a cut scene-setter.
- **Ending:** a cut closing line, or a new CTA.
- **Length:** cut or expanded.
- **Wording:** a word swapped for a plainer or more personal one.
- **Stance:** an opinion added, softened or made their own.
- **Facts:** a fact or detail corrected or added.
- **Links and format:** a link moved or removed, line breaks.

A **rule** is the general version of a change, written so it applies to next week's posts: "End on the practical point. Don't add a warning line after it (cut: 'The people at risk are the ones who never try it.')." Not "In last Tuesday's post, remove the last line."

Weigh them:
- **The same change in two or more posts** is a rule.
- **A one-off change** is a rule only if it's clearly about voice or format, not about that post's content (a corrected fact is a lesson for checking sources, not a voice rule). Otherwise, note it under "Watching" and wait for it to happen again.
- **Facts the owner added from their own knowledge** never become rules that invent facts. Note them so the posts leave room for their view.
- **A change that contradicts an existing rule:** the newer behaviour wins. Replace the old rule and say so.
- **CTA or format changes** (a new sign-off, where links go, a link removed from a Note) also go into `config/engine.yaml` or the social-posts Skill's CTA rules, because that's where those live.

## 3. Add them to the voice guide

In `voice.md` → **Learned from edits**, each rule is one bullet:

`- {rule}. ({before} → {after}; {run}, {date}) [confirmed | proposed]`

Use **[confirmed]** when the owner has agreed, and **[proposed]** when an unattended run added it. The social-posts Skill follows both. A proposed rule becomes confirmed when the owner says so, and is deleted if they say it's wrong. Keep the section short: merge rules that say the same thing, and keep the best example.

Under **Watching**, keep one-off changes that aren't rules yet (one line each). Promote one to a rule when it happens again, or drop it after four weeks.

Then add every Buffer id you took into account (edited, unchanged and deleted ones whose run is final) to `runs/edits-log.json`: `{"buffer_id", "run", "state", "learned_on"}`.

## 4. Tell the owner

- **When the owner is in the conversation:** show the proposed rules (each with its before → after) and ask which to keep. Mark the ones they keep [confirmed], reword any they correct, and drop the rest.
- **In an unattended weekly run:** don't ask. Add them as [proposed] and list them in the run README under **Voice rules learned from your edits**, so they can say "drop the rule about X" or "confirm the edit rules".

## Rules

- Learn from the owner's changes only. Never infer a rule from a post the engine wrote and the owner didn't touch, apart from noting it went out unchanged.
- Rules describe how they write. They never add facts, quotes or claims to future posts.
- Pending posts aren't learned from until they're sent.
- Commit `voice.md`, the `edits.json` files and `runs/edits-log.json` with the run.
