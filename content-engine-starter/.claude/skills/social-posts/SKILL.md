---
name: social-posts
description: Writes the author's LinkedIn posts, X post and Substack Note from a trend report, in their voice, with the right CTA for each channel. Use in the content engine after trend-report, or when asked to draft social posts from a brief or article.
license: Complete terms in LICENSE.txt
---

# Social posts

Writes the week's posts from `report.md`, in the author's voice (`config/engine.yaml` → `author`), one per draft slot in `config/engine.yaml` → `drafts`. Output goes to `posts.json` (for Buffer) and `posts.md` (for reading).

## Before writing

1. Read `report.md`. It is the only source of facts. Nothing goes in a post that isn't in it.
2. Read `references/voice.md` in full, then `references/samples.md` (the author's best posts, ranked). Write like the top three there, not like a LinkedIn template.
3. Read `config/engine.yaml` → `cta` for each channel's call to action.

## The posts

| Key | Channel | Goes with | Length | Shape |
| --- | --- | --- | --- | --- |
| `linkedin_infographic` | LinkedIn | the infographic | 90–160 words | News hook (≤ 12 words) → a number → the turn → the author's view → CTA |
| `linkedin_carousel` | LinkedIn | the carousel PDF | 70–130 words | A different hook from the infographic post → why swipe → CTA |
| `x_post` | X | the infographic | ≤ 270 characters including the link | One sharp claim + one fact + link |
| `substack_note` | Substack Notes | the infographic | 60–150 words | Conversational, like telling a peer what you noticed this week → CTA |

Only write the keys that appear in `config/engine.yaml` → `drafts`.

## CTAs

- **LinkedIn (`cta.linkedin`, type follow_save).** End both LinkedIn posts with `cta.linkedin.lines`, with `{author.name}` and `{author.linkedin_url}` filled in from the config, each on its own line, after a blank line. No comment keyword, no lead-magnet offer.
- **Substack Note (`cta.substack`).** End with `cta.substack.line`. No link needed; Notes show a subscribe button.
- **X (`cta.x`).** End with `cta.x.line`.

## Rules

- **Facts only from `report.md`,** and keep their numbers exact. A post may leave a fact out. It may not round it, stretch it or add one.
- **One idea per post:** the report's controlling idea, through its chosen angle.
- **The first line earns the second.** Specific beats clever: a number, a named change, a claim someone could disagree with. A question opener only if the next line answers it with data ("Is the CMO role dying? The data seems to suggest so."). Never "In today's world", "Let's talk about", or "Here's the thing".
- **Spelling per `author.language`.** No hashtags. No emoji except the ➕ and 🔖 in the LinkedIn CTA lines, and one 👇 if pointing to the comments.
- **No links in LinkedIn post bodies** (they cut reach), except the profile link in the CTA. If a source matters, write "link in the first comment" and put the URL in `first_comment`.
- **Pass every post through the no-ai-slop Skill** (edit mode, preserve voice) before saving. Re-check lengths afterwards.

## Output

`posts.json`:
```json
{
  "linkedin_infographic": {"text": "...", "alt_hooks": ["...", "..."], "first_comment": "" },
  "linkedin_carousel":    {"text": "...", "alt_hooks": ["...", "..."], "first_comment": "", "document_title": "≤ 60 characters, shown on the carousel post"},
  "x_post":               {"text": "..."},
  "substack_note":        {"text": "..."}
}
```

`posts.md`: each post under its key as a heading, with the alternative hooks listed under it, so the author can swap a hook in Buffer.
