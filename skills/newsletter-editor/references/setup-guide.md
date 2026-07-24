# Setup Guide

Read this file when running Phase 1 (initial setup) of the newsletter-editor skill. The goal is to collect enough user context to produce personalised output on every future run, then write the result to a config file the skill will read automatically on subsequent invocations.

## How to run setup

Walk the user through the questions below in order. Ask them conversationally, one or two at a time. Do not dump all questions at once. Explain briefly why each matters if the user seems unsure.

After collecting answers, write them to `newsletter-config.md` using the template at the bottom of this file. Show the config to the user and ask them to confirm before proceeding to Phase 2.

## The seven setup questions

### 1. Newsletter name and URL

Ask for the newsletter's name and the URL (if it has one). This is used in the draft output header and nowhere else, it grounds the writing in a real publication rather than an abstract one.

### 2. Niche and core topic

Ask: "What is this newsletter about? Give me the niche in one sentence."

Probe for specificity. "AI" is too broad. "AI for B2B marketing leaders" is a working niche. "Marketing" is too broad. "Demand generation for SaaS founders" is a working niche. If the user gives a vague answer, ask what audience they are writing for and what the reader is supposed to get out of it.

### 3. Audience

Ask: "Who is the reader? Describe them in one or two sentences, their role, their level of expertise, what they care about."

The answer shapes technical depth, examples, and tone. A newsletter for junior marketers reads differently from one for heads of marketing at listed companies.

### 4. Voice rules

Ask: "What are the non-negotiables for how this newsletter sounds? Things you always do or never do."

Examples to offer if they need prompting:
- UK English or US English
- Em dashes allowed or banned
- Hype language allowed or banned (game-changing, revolutionary, unlock)
- First-person mandatory or optional
- Paragraph length preference (short blocks vs. longer flowing prose)
- Tone (strategist, teacher, contrarian, practitioner, journalist)

Capture whatever they give. These become hard constraints in the drafting guides.

### 5. Section titles

Ask: "What do you want the two sections called?"

Defaults are "This Week's Top News" and "Thought Leadership Article." Most users will want something closer to their own brand. Offer examples:
- "The Weekly Briefing" + "Long Read"
- "What's New" + "The Essay"
- "Five Stories" + "My Take"

Whatever they choose, write it exactly as they want it to appear on the page.

### 6. Article length target

Ask: "How long should the thought leadership article be? Short (800–1,200 words), medium (1,200–1,800 words), or long (1,800–2,500 words)?"

Medium is the default if they have no preference. Explain briefly that articles much longer than 1,800 words start to feel AI-authored to readers.

### 7. Publication day

Ask: "What day of the week does the newsletter go out?"

This is used to date the draft file correctly and, optionally, to frame "this week" language in the news section.

## Writing the config file

Once all seven answers are collected, write `newsletter-config.md` to the user's current working directory using this exact template. Fill in the bracketed fields with the user's answers.

```markdown
# Newsletter Config

**Newsletter name**: [name]
**URL**: [url or "none"]
**Publication day**: [day of week]

## Niche
[one-sentence niche description]

## Audience
[one-two sentence audience description]

## Voice rules
- [rule 1]
- [rule 2]
- [rule 3]
- [etc, all voice rules collected, as bullet points]

## Section titles
- **News section**: [name]
- **Article section**: [name]

## Article length target
[short / medium / long, and the word range]

## Notes
[anything the user volunteered that doesn't fit the categories above]
```

Save this file to the current working directory. In Claude Code, also offer to save a copy to `~/.newsletter-editor/newsletter-config.md` so it persists across projects. Ask the user if they want this.

## Confirming with the user

After writing the file, show the user the full config and ask: "Is this right? Anything you want to change before we run your first draft?"

Only proceed to Phase 2 once they confirm. Setup is a one-time investment, getting it wrong here pollutes every future draft.

## Updating the config later

If the user wants to change their config later (new voice rule, different section name, tweaked niche), offer to open `newsletter-config.md` and walk them through edits. Do not rerun the full setup sequence for minor changes.
