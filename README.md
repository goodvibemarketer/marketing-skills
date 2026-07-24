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

---

## Install

### Claude Code (one command)

```bash
/plugin marketplace add goodvibemarketer/marketing-skills
/plugin install newsletter-editor@goodvibemarketer-marketing-skills
/plugin install b2b-landing-page@goodvibemarketer-marketing-skills
```

That is it. Claude Code will now use each skill automatically when you ask to draft a newsletter or build a landing page.

### Claude.ai (ZIP upload)

1. Download this repo as a ZIP
2. Extract it and find the skill folder you want (`skills/newsletter-editor/` or `skills/b2b-landing-page/`)
3. ZIP that folder on its own
4. In Claude.ai, go to Settings → Customize → Skills → Create skill
5. Upload the ZIP

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
- Reach me on [LinkedIn](https://www.linkedin.com/in/andy-goodvibemarketer) (replace with actual URL) for bigger conversations
- The skill is open source under MIT. Fork it, modify it, make it yours.

---

## What is next

Two more skills in the pipeline for this repo:

- **`contrarian-reframer`**, takes generic marketing copy and rewrites it using a contrarian reframe structure
- **`ai-marketing-audit`**, runs a four-step audit against any marketing setup you describe and returns a prioritised action plan

Follow the repo to get notified when they ship.
