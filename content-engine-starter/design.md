# Brand design system (for graphics)

The source of truth for every graphic this repo makes. The `engine-setup` Skill fills in the parts marked `TODO` from your Claude Design System, your website or colours you give it. Everything else is the house style that makes the graphics work in a feed; change it only on purpose.

## Colour tokens

Use these names in every graphic. Map your brand to them; don't invent new ones.

```css
:root {
  --canvas: TODO;          /* page background, never pure white */
  --surface-card: TODO;    /* cards; add a 1px --hairline border */
  --surface-strong: TODO;  /* neutral bars and fills */
  --surface-dark: TODO;    /* dark emphasis cards and the carousel's last slide */
  --ink: TODO;             /* headlines and main text */
  --body: TODO;            /* body copy */
  --muted: TODO;           /* captions, sources */
  --on-dark: TODO;         /* text on --surface-dark */
  --on-dark-soft: TODO;
  --highlight: TODO;       /* the highlighter brush behind headline keywords */
  --accent: TODO;          /* charts: the highlighted bar or slice, step markers */
  --accent-text: TODO;     /* accent as text: big numbers, labels (must pass contrast on --canvas) */
  --hairline: TODO;        /* 1px borders */
  --grid-line: TODO;       /* notepad grid, e.g. rgba(20,20,19,0.045) */
}
```

## Type

- Display (headlines, big numbers): TODO font name, weight. Font files in `brand/fonts/` if it isn't a system font; load with `@font-face`.
- Sans (body, labels, buttons): TODO font name.
- `font-variant-numeric: lining-nums` everywhere. Sentence case. No exclamation marks. No emoji.
- **Minimum sizes on infographics** (CSS px on the 1080×1350 layout): nothing under 20px, body and list text 22px+, and the sans in a medium weight (500), not regular, for anything under 24px. Infographics are exported at 2× (2160×2700) so text stays sharp on phones.

## Signatures

- Faint notepad grid on the canvas: 36–40px squares in `--grid-line`. (Delete this line if your brand wants a plain background.)
- Highlighter: an irregular brush stroke in `--highlight` (opacity ~0.45 on light, ~0.7 on dark) behind 1–3 key words of the headline.
- Charts and numbers: the highlighted series is `--accent`, the rest `--surface-strong`; big numbers in `--accent-text`.
- Icons and illustrations: thin stroke line art, round caps, `--ink` with one accent. No filled clip art.

## Charts and illustration

- The chart type follows the data: see the Chart chooser in `.claude/skills/linkedin-infographic-builder/SKILL.md`. Bars only for comparing or ranking categories.
- Every infographic and every carousel cover has a line-art hero illustration of the headline's idea.

## Headlines (every infographic and every slide)

People are scrolling. If the headline isn't understood in two seconds, they keep scrolling.

- **No eyebrow.** Nothing above the headline: no kicker, category, date line or label. Dates and sources go in the body.
- **Name the subject in plain words** ("ChatGPT ads", "HubSpot", "Google's AI Mode"), ideally in the first five words.
- **Then say what's interesting about it**: a claim, a number or a tension. "ChatGPT ads are coming. Now you can measure them."
- **No abstract or clever headlines** that only make sense after reading the post. Fails: "The ad format is new. The measurement is the news."
- **The stranger test.** Someone who hasn't seen the news reads only the headline. Do they know what it's about and why they'd care?
- **Every carousel slide headline stands on its own.**

## Sign-off strip (footer of every graphic)

Full width at the bottom, 1px `--hairline` rule above.
- Left: TODO `brand/headshot.jpg` as a 64–72px circle and `{author.name}` in the display font, **or** `brand/logo.svg` for a company page.
- Right: TODO where people find more, e.g. newsletter URL or website, with its small mark if you have one.

## Channel CTAs

| channel | CTA block |
| --- | --- |
| `linkedin` | Follow/save card. Left: "FOUND THIS USEFUL?" in sans caps, `--accent-text`. Right: a filled `--ink` pill with a plus icon and "Follow {author.name}", and an outlined pill with a bookmark icon and "Save". On the carousel's last slide (dark): "Found this useful?" with the highlighter on "useful?", then the same two pills stacked and inverted |
| `substack` | Subscribe card. Left: "SUBSCRIBE FREE" and your newsletter URL large in the display font. Right: TODO your free offer in three ticked lines (e.g. what new subscribers get). On the carousel's last slide (dark): headline "Found this useful? Subscribe.", URL, then a FREE box and (if you have one) a PAID box, each a heading plus three ticks |
| `x` | Same as `substack` |
