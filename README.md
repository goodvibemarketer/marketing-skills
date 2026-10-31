# marketing-skills

A portfolio of [Claude Skills](https://docs.claude.com/en/agents-and-tools/agent-skills) built for marketers, newsletter operators, and content teams who want to stop writing from scratch every week and start editing a pipeline instead.

Built by [Andy at GoodVibeMarketer](https://goodvibemarketer.com).

---

## What is a Claude Skill?

A Skill is a packaged capability Claude loads on demand when you ask for a specific kind of task. Install a skill once, and from then on Claude automatically uses it when your request matches. Skills work in Claude.ai, Claude Code, and the Anthropic API.

[More on Skills here](https://docs.claude.com/en/agents-and-tools/agent-skills).

---

## Skills in this repo

### `newsletter-editor`

Drafts a complete weekly newsletter from a rough drop file of notes, links, and themes.

**What it produces:** Two sections, a synthesised news roundup and a full thought leadership article (1,200–1,800 words). Both drafted to your configured voice, niche, and audience.

**What it changes:** You stop writing your newsletter. You start editing it.

**How it works:** Runs in two phases. The first time you use it, it walks you through a seven-question setup (niche, voice rules, section titles, article length target). That gets written to a `newsletter-config.md` file. From then on, every weekly run reads your config, ingests a drop file of rough inputs, and outputs a publication-ready draft.

See [`skills/newsletter-editor/`](./skills/newsletter-editor/) for the full skill, including reference files and worked examples.

### `b2b-landing-page`

Plans and builds a complete B2B landing page — from strategy through to the built page — for any product sold to a business.

**What it produces:** A reviewable brief (objective, message hierarchy, section-by-section copy, a justified form spec, and visual direction), then, on approval, the built page itself.

**What it changes:** You stop shipping pages that give the visitor five things to do and open with a claim nobody was promised. You start shipping pages built structure-first, with a 1:1 attention ratio and no invented proof.

**How it works:** Runs in two phases with a review point between them. Phase 1 gathers context in two short beats, makes the structural decisions, writes the copy, and delivers a brief that opens with every assumption it made — then stops. If you only wanted a document to hand to a designer, that is the finish line. Phase 2, on your approval, enforces the constraints and builds the page, ending with a pre-publish checklist and a list of what you still owe it. It never invents statistics, customer names, quotes, logos, or product screenshots — gaps are marked, not faked.

See [`skills/b2b-landing-page/`](./skills/b2b-landing-page/) for the full skill, including the brief schema and design rules reference files.

### `linkedin-infographic-builder`

Turns one piece of content into a single, on-brand infographic for LinkedIn.

**What it produces:** One 1080x1350 px PNG — the portrait size that fills the most screen on LinkedIn mobile — styled by your design system, with your face and name in the footer.

**What it changes:** You stop posting plain-text takes that scroll past. You start posting one reusable idea a buyer can screenshot into their own deck.

**How it works:** Reads your active design system for tokens, then builds the graphic in HTML/CSS and rasterises it with a headless browser at the exact output size. House style is a faint notepad grid, a brush-stroke highlight on one headline keyword, thin line-art metaphors and a single dark band for the big idea. It never invents a statistic: if your content has no data, it draws a framework or before/after diagram instead.

See [`skills/linkedin-infographic-builder/`](./skills/linkedin-infographic-builder/) for the full skill.

### `infographic-animator` (add-on to `linkedin-infographic-builder`)

Turns the infographic you just made into a GIF.

**What it produces:** One looping GIF sized for LinkedIn, plus a lighter cut under Substack Notes' size limit, and the timeline file so you can re-render after a design change.

**What it changes:** The graphic assembles in the order you want it read, so the first two seconds in the feed follow your argument instead of showing everything at once.

**How it works:** Loads the infographic's own HTML in a headless browser, applies a timeline of effects (highlighter wipes, counting numbers, line art drawing itself, sections fading in, or a seamless loop of moving parts) and writes the frames to a GIF. Nothing is redesigned: the last frame is the static infographic. Install it alongside `linkedin-infographic-builder`; on any other 1080x1350 graphic it falls back to simpler fades from the PNG.

See [`skills/infographic-animator/`](./skills/infographic-animator/) for the full skill.

### `linkedin-carousel-builder`

Repurposes one long-form piece into a LinkedIn carousel.

**What it produces:** A 6-10 page PDF at 1080x1350 px per page, ready to upload as a LinkedIn document post, plus a PNG of each slide, a document title, a caption draft and two alternative hooks.

**What it changes:** One article stops being one post. It becomes the swipe that carries a single idea to its point.

**How it works:** Plans the carousel before designing anything — picks the one strongest idea out of the source and leaves the rest — then applies your design system and renders the PDF. Every number shows its source on the slide, and the last slide is a follow or subscribe CTA.

See [`skills/linkedin-carousel-builder/`](./skills/linkedin-carousel-builder/) for the full skill.

### `ai-marketing-trend-radar`

Finds what is actually being discussed on your topic in the last seven days, and turns it into things to post.

**What it produces:** A ranked report in chat, a shareable page and an A4 PDF, all built from one data file. Each trend carries what happened, why your audience should care, the conversation with verbatim quotes, and three angles — hot take, practical, contrarian — each with a suggested format and a date to post it.

**What it changes:** The weekly "what should I write about" problem stops being a blank page. You start from six ranked trends with the receipts attached.

**How it works:** Six agents search Hacker News, trade press, the wider web, company launches, new research and data, and newsletters in parallel, then everything is filtered against your audience, clustered, and scored 0-100 on signal, audience relevance, content potential and momentum. A trend needs two sources to rank; a story from one source goes under rising signals. It needs no paid tools or API keys: everything runs on Claude's web search and the free Hacker News API. Topic, audience, region and branding are settings, so the same skill runs a radar on anything.

See [`skills/ai-marketing-trend-radar/`](./skills/ai-marketing-trend-radar/) for the full skill.

### `sketch-explainer`

Draws the one big idea in an article as a hand-drawn, pen-on-paper explainer.

**What it produces:** One PNG (portrait, square or landscape) with a handwritten title, wobbly boxes and arrows, highlighter on the key words, doodle icons and one punchline.

**What it changes:** The simple visual people save, without opening a design tool.

**How it works:** Picks a layout from the shape of the idea (a list, this-versus-that, a 2×2, a flow, an equation or one big number), writes 25 to 60 words, then renders real text in handwriting fonts with every line around it drawn by rough.js. Your pen and highlighter colours and an optional signature go in its "Make it yours" block.

See [`skills/sketch-explainer/`](./skills/sketch-explainer/) for the full skill.

### `notebook-notes`

Turns an article's framework, findings or process into a photo-style page of handwritten notebook notes.

**What it produces:** One PNG of a notebook page lying on a desk: ruled, dotted or grid paper, spiral or gutter binding, neon highlighter, coloured pen and circled numbers.

**What it changes:** Gives you the "photo of my notes" post that gets saved, from any article.

**How it works:** Numbered notes, a mind-map flow, a hub or a pyramid, picked by the shape of the content, with 60 to 140 words. Paper, binding, desk, handwriting and pen vary each time.

See [`skills/notebook-notes/`](./skills/notebook-notes/) for the full skill.

### `ai-slop-pattern-linter`

Edits a draft into sharper, more human writing while keeping your voice, or names the AI-slop patterns without rewriting.

**What it produces:** The edited draft plus a short note on what changed, or, in detect mode, each pattern found with the line it is in and the fix.

**What it changes:** Drafts stop reading as machine-made, without losing the bluntness and digressions that make them yours.

**How it works:** Reads your voice first and makes the minimum effective edit. A word list, often-empty phrases and about fifteen named patterns, each with a worked before and after, all in one readable file you can change. House terms you list in its "Make it yours" block are never cut.

See [`skills/ai-slop-pattern-linter/`](./skills/ai-slop-pattern-linter/) for the full skill.

### `content-engine-starter`

The full weekly content engine from the [AI Marketing Engineer's Guide](https://goodvibemarketer.substack.com): trend radar, fact-checked trend report, posts in your voice, a branded infographic and carousel, all saved to Buffer as drafts by a Claude Code routine every Monday.

**What it produces:** A private GitHub repo that runs your content prep every week, with nothing posted until you approve it.

**How to use it:** This one is a whole project, not a single Skill. Make a private repo, open it in Claude Code and ask Claude to copy the [`content-engine-starter/`](./content-engine-starter/) folder into it. The step-by-step setup, tuning and automation are in the guide for paid subscribers.

**Licence:** Not MIT. The kit has its own licence in [`content-engine-starter/LICENSE.txt`](./content-engine-starter/LICENSE.txt).

---

## Install

### Claude Code (one command)

```bash
/plugin marketplace add goodvibemarketer/marketing-skills
/plugin install newsletter-editor@goodvibemarketer-marketing-skills
/plugin install b2b-landing-page@goodvibemarketer-marketing-skills
/plugin install linkedin-infographic-builder@goodvibemarketer-marketing-skills
/plugin install linkedin-carousel-builder@goodvibemarketer-marketing-skills
/plugin install ai-marketing-trend-radar@goodvibemarketer-marketing-skills
/plugin install sketch-explainer@goodvibemarketer-marketing-skills
/plugin install notebook-notes@goodvibemarketer-marketing-skills
/plugin install ai-slop-pattern-linter@goodvibemarketer-marketing-skills
```

That is it. Claude Code will now use each skill automatically when you ask to draft a newsletter, build a landing page, turn a post into an infographic, carousel, sketch or notebook page, tighten a draft, or find out what is trending this week.

### Claude.ai (ZIP upload)

The easiest route is the ready-made ZIPs, each with an install guide, at [goodvibemarketer.com/skills](https://www.goodvibemarketer.com/skills/). Or build one yourself:

1. Download this repo as a ZIP
2. Extract it and find the skill folder you want (`skills/newsletter-editor/`, `skills/b2b-landing-page/`, `skills/linkedin-infographic-builder/`, `skills/linkedin-carousel-builder/`, `skills/ai-marketing-trend-radar/`, `skills/sketch-explainer/`, `skills/notebook-notes/` or `skills/ai-slop-pattern-linter/`)
3. ZIP that folder on its own
4. In Claude.ai, go to Settings → Customize → Skills → Create skill
5. Upload the ZIP

### Make it yours

Each skill except `newsletter-editor` opens with a **Make it yours** block in its `SKILL.md`: your company, audience, voice and brand details. Fill it in once after installing and every run starts from your business. Those skill folders also carry a short PDF guide to installing and customising them. `newsletter-editor` asks its own setup questions on first run instead.

### Claude API

Upload the skill via the `/v1/skills` endpoint. See [the Anthropic docs](https://docs.claude.com/en/build-with-claude/skills-guide) for the current syntax.

---

## First-run walkthrough

The first time you trigger the skill, by saying something like "help me draft my weekly newsletter" or "run the newsletter editor", it will notice you have no config and walk you through setup. Expect about five minutes of questions. Once the config is written, every future run takes one input (a drop file) and gives you back a full draft.

Example drop file format is in [`skills/newsletter-editor/examples/sample-drop-file.md`](./skills/newsletter-editor/examples/sample-drop-file.md). You do not need to match it exactly. The skill accepts loose notes, bullet points, or prose.

---

## Why this exists

Most newsletter operators are writing every word from scratch, every week, forever. It is slow, it is exhausting, and it does not scale.

I built this skill because I got tired of being the writer. I wanted to be the editor. The difference matters: a writer generates; an editor directs. One scales; the other does not.

This skill democratises the pattern. Configure it once with your voice and niche. Feed it a drop file every week. Get a publication-ready draft back. Edit, don't write.

If you run a newsletter and you are still drafting from an empty page every Monday morning, this is for you.

---

## Who builds this

I write [GoodVibeMarketer](https://goodvibemarketer.com), a weekly newsletter on practical AI marketing for B2B teams. The newsletter itself is drafted using the pipeline this skill was carved out of.

If you want a weekly breakdown of how marketers are actually using AI in the field (not speculating about it), the newsletter is the place. [Subscribe here](https://goodvibemarketer.com/subscribe).

---

## Feedback and issues

- File an issue on this repo if something breaks or the skill produces weird output
- Reach me on [LinkedIn](https://www.linkedin.com/in/goodvibemarketer) for bigger conversations
- The skills in `skills/` are open source under MIT. Fork them, modify them, make them yours. `content-engine-starter/` has its own licence.

---

## What is next

Two more skills in the pipeline for this repo:

- **`contrarian-reframer`**, takes generic marketing copy and rewrites it using a contrarian reframe structure
- **`ai-marketing-audit`**, runs a four-step audit against any marketing setup you describe and returns a prioritised action plan

Follow the repo to get notified when they ship.
