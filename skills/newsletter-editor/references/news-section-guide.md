# News Section Guide

Read this file when drafting Section 1 (the news roundup) in Phase 2. This section is the briefing half of the newsletter, five news stories from the user's niche, synthesised into a single connecting argument, with a short pattern-recognition close.

## The core structure

The news section is not a list of five disconnected items. It is five items bound together by a thesis. Start from the thesis, then build the five items to support it.

### Length and shape

- **Total length**: 500–700 words
- **Opening**: one sentence establishing the week's connecting argument
- **Five stories**: 80–120 words each, each one a single paragraph
- **Closing**: two to three sentences identifying the pattern across the five

Do not use bullet points. Do not use subheadings per story. Each story is its own paragraph with a bolded lead-in phrase or a strong opening sentence naming the subject.

## The five-step process

### Step 1, Find the connecting thesis

Read the drop file. Look for the through-line across the five news items. What do these stories, taken together, actually say about the state of the niche this week?

Good theses are specific and slightly contrarian:
- "The gap between brands adopting AI and brands reorganising around it keeps widening."
- "Trust is becoming the differentiator, not capability."
- "The traffic model is breaking, the agent model is forming."

Bad theses are generic:
- "AI is changing marketing."
- "Lots of stuff happened in martech this week."

If the five stories in the drop file do not support a single thesis, pick the four that do and drop the fifth. A coherent briefing beats a complete one.

### Step 2, Write the opening line

One sentence. Establishes the thesis. No preamble, no throat-clearing, no "this week we saw." Just the argument.

Examples:
- "This week is about one reality settling in: the traffic model is breaking, the agent model is forming, and the gap between brands reorganising and brands adopting keeps widening."
- "This week is about one line being drawn: whose side is your AI on?"

Match the user's voice rules from the config. If they have a first-person mandatory rule, weave yourself in ("This week I'm watching..."). If not, stay in third-person observational mode.

### Step 3, Draft each story

For each of the five stories, produce a single paragraph that does four things in sequence:

1. **State the news.** The who, what, when, compressed into the first sentence.
2. **Give one concrete data point or quote** that shows you actually read past the headline. A number, a named source, a specific detail.
3. **Interpret the strategic read.** What does this actually mean, not just what happened. This is where voice shows up.
4. **Close with the implication for the reader.** Why should the reader in the user's defined audience care. Frame it in terms of their work, not the industry in the abstract.

Each paragraph should open with a distinctive, concrete lead rather than a generic "In other news." The lead can be the company name, the specific product, the specific figure, or a short thematic framing.

### Step 4, Write the pattern-recognition close

Two to three sentences at the end. Name the pattern that ties the five stories together. This is the thesis stated again, but now earned, the reader has seen the five pieces of evidence, and now you are telling them what the evidence means.

Do not summarise. Do not recap. Interpret.

Examples:
- "The pattern: distribution is fragmenting. Each surface now has its own rules. Brands that treat each surface uniformly lose on every one."
- "The pattern: trust is becoming the differentiator. Everyone has agents now. The question is whether yours work for you, and whether you can prove it."

## Voice application

Apply the voice rules from `newsletter-config.md` to every sentence. Read `voice-patterns.md` for the generic rules. The most common non-negotiables to respect:

- **If UK English is configured**, never use American spellings (optimise, behaviour, organise, programme, favour).
- **If em dashes are banned**, replace with commas, full stops, or colons.
- **If hype language is banned**, strip words like game-changing, revolutionary, next-gen, unlock, seamless, unprecedented.
- **If first-person is mandatory**, use "I" at least once in the opening or close.

## What not to do

- **Do not editorialise beyond the thesis.** The news section is briefing, not essay. Keep interpretation tight.
- **Do not cite sources unless the drop file provides them.** Do not fabricate a quote, a statistic, or a named source. If the drop file does not contain a specific number, do not invent one.
- **Do not use hedging language** ("it could be argued," "some might say," "one interpretation is"). Commit to the read.
- **Do not use transition words between stories** that suggest a list ("firstly," "secondly," "meanwhile"). Each story stands alone as a paragraph.

## A complete worked example

See `examples/sample-output.md` for a full news section drafted from `examples/sample-drop-file.md`. Study the interplay between drop-file inputs and final output, especially where the drafted version adds interpretation the drop file did not contain, and where it stays strictly faithful to the source material.
