# Article Guide

Read this file when drafting Section 2 (the thought leadership article) in Phase 2. This is the long-form half of the newsletter, a full 1,200–1,800 word piece (or whatever length the config specifies) with a contrarian reframe, opinionated section headings, and a practical close.

## The core structure

Every article follows the same five-beat arc. Do not skip beats. Do not reorder them without reason.

1. **Contrarian hook**, the reframe lands in the first six lines
2. **First-person thread**, the author's stake in the topic is established early
3. **The argument**, three to five opinionated sections, each with a position-taking heading
4. **The evidence**, concrete examples, data, or lived experience supporting each section
5. **Practical close**, "what changes tomorrow morning" for the reader, not a bullet-point list

## The contrarian reframe structure

This is the single most important pattern. Every article opens the same way in spirit, even if the words change:

1. **State the common belief.** What most people in the niche currently think or say about this topic.
2. **Introduce the tension.** Name the thing that the common belief misses, misunderstands, or oversimplifies.
3. **Reveal the deeper layer.** The actual point. The reframe.

This must land within the first six lines. Readers decide whether to stay in the first paragraph.

**Example opening:**

> There is a narrative floating around that AI is a shortcut.
>
> That it lets you skip the hard bits.
> That it replaces depth with speed.
>
> That has not been my experience.
>
> Building [X] did not help me avoid learning. It forced it.

That opening does all three beats in under 40 words. Common belief (AI is a shortcut), tension (my experience contradicts it), reframe (AI forces learning rather than replacing it).

## Drafting the article: step by step

### Step 1, Find the core argument in the drop file

Read the drop file. Look for the single argument the user wants to make this week. It might be stated as a theme. It might be buried in a few notes. It might be implied by the news stories they chose to include.

Whatever it is, compress it into one sentence. This is the spine. If you cannot write the spine in a single clear sentence, the article will not hold together. Ask the user to clarify before drafting.

### Step 2, Identify the common belief to reframe

For the argument you identified, what does the audience defined in the config currently think about this topic? What is the conventional wisdom? That is the common belief you will reframe in the opening.

Do not make up a strawman. The common belief has to be something the reader will actually recognise as the dominant view in their niche.

### Step 3, Draft the opening (first six lines)

Using the contrarian reframe structure above:
- Line 1–2: the common belief, stated plainly
- Line 3–4: the tension, with a first-person cue
- Line 5–6: the reframe

Short lines. White space between beats. No warm-up.

### Step 4, Outline the argument

Plan three to five sections that build the argument. Each section heading must take a position, not describe a topic.

**Good section headings** (take a position):
- "Most Marketing Teams Don't Have an AI Problem. They Have a Clarity Problem."
- "AI Does Not Intuit Brand. It Responds to Articulation."
- "Removing Fear Increases Velocity."

**Bad section headings** (describe a topic):
- "How AI is Changing Marketing"
- "The Role of Brand in AI Content"
- "Thoughts on Velocity"

Each section should take 200–400 words. If a section runs longer than 400 words, split it. If shorter than 150, fold it into the next one.

### Step 5, Draft each section

Inside each section:
- Open with the heading's claim, stated clearly
- Give one concrete example, data point, or lived experience that supports it
- Reveal the implication, what this means for the reader, not for the industry

Apply the voice rules from `newsletter-config.md`. Read `voice-patterns.md` for paragraph-length, sentence-rhythm, and banned-language rules.

Use short paragraphs (one to three lines). Use standalone compression sentences, four to ten words, to mark pivots.

**Example of the expand-compress rhythm:**

> AI does not guess taste.
>
> It executes clarity.
>
> The more specific my instructions became, the better the output. I moved from "make it feel premium" to "align the results header hierarchy with the consultancy site, standardise button states, and tighten section spacing to match the 24px grid." One version produced generic output. The other produced brand-coherent output.

Three short paragraphs. One compression sentence. One expand paragraph. The rhythm matters.

### Step 6, Write the practical close

Every article ends with "what changes tomorrow morning", framed for the reader, not as a summary of what the author said.

Do not use bullet points. Do not use numbered lists. Do not say "to recap" or "in conclusion." The close is a final argument, not a summary.

A good close does three things:
1. Names the shift the reader should now see
2. Names the concrete thing that is different tomorrow because of it
3. Leaves the reader with a question or frame they carry forward

**Example close:**

> The shift is not about adoption. It is about redesign.
>
> Tomorrow morning, the question on your desk is no longer "which tool do we buy" but "which workflow do we rebuild."
>
> Most teams will keep buying. A few will rebuild. The gap between them is the thing worth watching.

## The first-person thread

Every article must contain a first-person thread. This is non-negotiable even in articles that are mostly analytical. The thread can be light, a single sentence describing what the author did, built, noticed, or lived through, but it must be there.

The first-person thread does two jobs:
1. It grounds the analysis in experience rather than abstraction.
2. It makes the article feel written by a human rather than generated.

Weave it into the opening or the first major section. Do not save it for the close, readers who bounce early will not see it.

## Personal texture (use sparingly)

If the user's config mentions personal texture they want to include (a hobby, a background detail, a recurring motif), use it at most once per article. Never lead with it. Always use it in service of the argument, not as decoration. If the drop file does not call for it, do not force it in.

## Article length management

Target the word count in the config:
- **Short**: 800–1,200 words, three sections
- **Medium**: 1,200–1,800 words, three to four sections (default)
- **Long**: 1,800–2,500 words, four to five sections

Articles that run materially over the configured length will feel AI-authored. Cut ruthlessly if the draft goes long. Each sentence earns its place or it leaves.

## What not to do

- **Do not use em dashes** if the config bans them. Use commas, full stops, or colons instead.
- **Do not use hype language.** No "game-changing," "revolutionary," "unlock explosive growth," "next-gen," or "seamless."
- **Do not hedge.** The article takes a position. Hedging signals uncertainty; uncertainty kills authority.
- **Do not summarise in bullet points at the end.** The practical close is prose, not a takeaway list.
- **Do not fabricate data or sources.** If the drop file does not contain a specific statistic, do not invent one.
- **Do not break the first-person thread.** Even one first-person anchor in a 1,500-word piece is enough; zero is too few.

## A complete worked example

See `examples/sample-output.md` for a full article drafted from `examples/sample-drop-file.md` using `examples/sample-config.md`. Pay attention to the interplay between the drop file's loose notes and the final article's opinionated structure.
