---
name: b2b-landing-page
description: Plans and builds complete B2B landing pages — strategy, message hierarchy, section-by-section copy, form specification, visual direction, and the built page. Use whenever the user mentions a landing page, LP, lead-gen page, demo-request page, campaign destination page, or squeeze page for a product sold to businesses, and whenever they ask for landing page copy, headlines, hero sections, or CTAs, or want an underperforming page rebuilt. Also use when a paid campaign needs a destination page. Trigger even if the user just says "build me a landing page" or "write a landing page" without saying B2B, as long as the buyer is a business. Runs in two phases — a reviewable brief, then the build — and stops after the brief if the user only wants a document to hand to a designer or developer. Do not use for blog posts, ads, emails, or general website pages.
---

# B2B Landing Page

Take a product and a campaign objective through to a built landing page, in two phases with a review point between them.

**Phase 1 — the brief.** Gather context, make the structural decisions, write the copy. Stop and show it.
**Phase 2 — the build.** On approval, enforce the constraints and build the page.

The gap between the phases exists because strategy errors are cheap to fix in a brief and expensive to find in a finished page. Don't skip it, and don't build during phase 1.

Reference files, read at the point they're needed:
- `references/brief-schema.md` — every field in the brief, and what to do when one is missing. Read before writing the brief.
- `references/design-rules.md` — constraint enforcement, section-to-component mapping, mobile rules, pre-publish checklist. Read before building.

---

## Why this skill exists

Most landing pages fail for reasons that have nothing to do with the writing. They give the visitor several things to do instead of one. They open with a claim the visitor was never promised. They ask a senior buyer for fifteen minutes before earning thirty seconds. Good sentences don't fix any of that.

So the work happens in order: understand the situation, make the structural decisions, write, then build. Copy written before the structural decisions is guesswork with good grammar, and a page built before the copy is decoration.

---

# Phase 1 — The brief

## 1. Take whatever context exists

The user may paste a product one-pager, a positioning doc, notes from a strategy session, or a single sentence. Accept any of it. Read it, map what it contains onto the schema, and never ask for a particular input format.

If a `profile-<product>.md` from a previous run is present or mentioned, load it — it holds the durable product facts and saves repeating them.

**Look for assets before assuming there are none.** If the surface has access to a folder, read it. Logos, product screenshots, case studies, brand guidelines and an existing brief may already be sitting there, and asking for something the user has already supplied is the fastest way to look careless. Record what's found in the §8.1 and §8.2 registers as `real`, and only specify placeholders for what's genuinely absent.

## 2. Ask in two beats, never one long interrogation

Three things stop the work if they're absent. Without them the brief would be invented rather than built:

1. **The page objective** — the business outcome the page exists to produce.
2. **The single conversion action** — the one thing a visitor can do, in the exact words that will appear on the button.
3. **Traffic source and funnel stage** — where visitors come from, and how much they already know. One question, two angles.

Everything else is inferable — but only *after* the product is known. That's why this happens in two beats. At cold start there is nothing to infer from, and asking for everything at once turns into an interrogation with a row of blank boxes.

**Beat one — orient. A fixed set, not a quota.**

Beat one asks for the three stops above, plus the product in one sentence if the user hasn't already given it. That's the entire set. Use selectable options wherever the answer set is predictable; keep it to one free-text box.

**If some are already answered, ask fewer.** A user whose opening message describes the product and names the CTA leaves two questions, and two questions is the correct beat one — not two plus two more promoted from beat two to round it out. Four is a ceiling, never a target. The shortest beat one that gets the stops answered is the best one.

**Nothing else belongs here.** The buyer and the buying committee, the pain, the competitive alternative, the objections, the proof assets, the tone, and the form composition are all beat two — every one of them inferable once the product is known, and every one better presented as a draft to correct than as a blank to fill. If a question feels natural to add because there's room, that is the signal it belongs in beat two.

**Beat two — draft, then ask for corrections.**

With the product known, infer the rest and present it as a filled-in draft to correct rather than blanks to complete: the primary buyer and what they're accountable for, the buying committee, the pain, the real alternative, the objections, the tone, and the form fields.

Propose the form as a specific short list with each field justified, not as a question about what to collect. *"Form: work email, company, monthly ad spend band — email to reach them, company because the audit is company-specific, spend band to scope it. Cut or add anything."* A user asked what their form should collect will tick more boxes than they need; a user shown three justified fields will usually accept them.

> "Here's what I've assumed. Correct anything wrong and I'll build from it.
> **Pain:** a customer is demanding a certificate before they'll sign.
> **Real alternative:** a spreadsheet someone in ops maintains by hand.
> **Committee:** Head of Security champions, CTO and Legal evaluate.
> **Objection to beat:** 'we'll do this in-house.'"

Being wrong here costs nothing — the user corrects a line. Being blank costs a lot: an open textarea labelled *"what's the single biggest pain your buyer feels?"* is the most expensive thing you can put in front of someone who came to save time.

**Proof is the exception — ask, don't infer, and ask for what exists today.** Proof assets are the one thing that can't be drafted, because inventing them is the failure the whole brief guards against. But how the question is framed decides the answer. A menu of proof types reads as a list of things a competent company ought to have, so people tick the ones they aspire to and the page ends up promising evidence nobody can supply.

Ask instead for what exists right now, in the user's hands, today — and say plainly that anything missing becomes a marked gap rather than something invented. Make "nothing yet" an easy and unembarrassing answer: an early-stage product with no logos, no quote and no metric is normal, and a page with honest gaps is more useful than one with fabricated proof. If the answer includes something that later turns out not to exist, it goes back to being a placeholder.

**Caps that hold in both beats:** never more than four questions in a turn, and never more than two free-text boxes. If more than four things seem necessary, the extras are inferable — draft them instead. And a cap is not a quota: asking two when two will do is better than asking four.

**Skip beat one entirely when context already exists.** If the user pastes a product one-pager, a positioning doc, or an approved brief, take the answers from it and go straight to beat two — or straight to the build if nothing is missing.

If the user can't name the traffic source — common, and fine — use `mixed-unknown` and apply §2.5 of the schema. Say plainly that a page which can't assume prior context is weaker than a matched one, rather than building it and implying otherwise.

For a rebuild, ask for the existing page. Reading it is faster than having it described, and it usually shows the structural fault immediately.

## 3. Make the structural decisions before writing a word

Three decisions, each recorded with its reasoning:

**The one thing above the fold.** A single sentence. If it takes two, it isn't one thing yet.

**The section order.** Built only from the fixed vocabulary below, following the stage rules. State any deviation rather than making it silently.

**The friction decision.** When the ask is large relative to how warm the traffic is — a live audit from a cold ad click, a demo booking from a first-time visitor — resolve it explicitly: *earn it* (more proof and objection handling before the form), *reduce it* (lower the ask), or *split it* (a smaller first step that qualifies into the real one).

**Recommend, don't override.** When the stated conversion action looks wrong for the traffic, build what was asked for and put the alternative next to it with the reasoning. The user knows things about their funnel that aren't in the brief, and a skill that quietly substitutes its own judgement for a stated decision is one the user stops trusting. Say what you'd do differently; let them decide.

## 4. Write the copy

Section by section, in the order set in step 3, following the copy rules below.

## 5. Deliver the brief and list every assumption

Save as `brief-<product-slug>-<page-slug>.md`.

Open with the assumptions — every field inferred rather than given, most-likely-wrong first. The user needs to see what was guessed, or they'll trust a page built on a wrong premise. A short honest list is worth more than a confident brief.

Also write the durable product facts to `profile-<product-slug>.md` — what the product is, who buys it, the alternatives, the proof assets, the brand tokens. Mention it exists so the next page doesn't start from zero. Never require it.

**Then stop.** Present the brief, name the open items, and wait. If the user only wanted a document to hand to a designer or developer, this is the finish line.

---

## Working with design systems and templates

Some surfaces let the user select a design system, a template, or both before the skill runs. Check what's in play before asking for anything, and never ask for something already supplied.

**A design system supplies the brand tokens.** Colours, typography, and component styling come from it — so skip the brand token questions entirely and record the system as the source in §7.5 rather than `DEFAULT`. Say which system is being used, so the user knows why they weren't asked. One check still applies: the conversion action needs clear contrast against its background. If the system's palette can't provide it, use an accent that can and record the deviation.

**A template supplies structure, and most of that structure has to go.** Landing templates ship with a navigation bar, a footer full of links, and two or three competing calls to action, because they're built for general marketing pages. Every one of those violates the constraints.

Keep the template's typography, spacing, and component styling. Strip its navigation, its footer links, its secondary CTAs, and any section that isn't in the section vocabulary. Then rebuild the section order from the brief — a template's default order is a generic argument, not this page's argument.

Tell the user what was removed and why. Someone who deliberately chose a template will notice its nav bar missing, and "removed to keep the attention ratio at 1:1" is a better answer than silence.

**Neither available?** Run the brand token cascade in schema §7.5 — ask for colours and fonts, then for a website URL, then fall back to a neutral default the user can restyle in one instruction.

---

## Section vocabulary

Fixed set. Build only from these:

`hero` · `proof-bar` · `problem` · `solution` · `how-it-works` · `outcome` · `objection` · `proof-detail` · `final-cta`

Sections can repeat and can be omitted. Only the type names are fixed — a page that seems to need something outside the set is usually a page trying to do two jobs.

| Stage | Structure |
|---|---|
| **Cold** | Problem framing before any offer. Longest page. Proof early, because trust starts at zero. |
| **Warm** | Problem compressed to a line. Lead with the mechanism. |
| **Bottom** | Shortest path to the form. Problem framing omitted. Objection handling stays. |

Objection handling survives at every stage. A buyer close to converting has more specific objections, not fewer.

---

## Copy rules

**Keep the inbound promise.** The hero must visibly keep whatever the visitor was told before arriving — the ad hook, the subject line, the search query, the salesperson's pitch. A hero that reads beautifully and matches nothing is the commonest reason a well-written page converts badly.

**One conversion action, one wording.** The CTA text is identical everywhere it appears. Varying it for rhythm reads as writing craft and behaves as three different offers.

**No claim without adjacent proof.** Every claim either sits next to a proof element from the register, or carries a visible `[PROOF NEEDED — describe what would prove this]` marker. Proof quarantined in a logo bar at the bottom isn't proof of anything specific.

**Never invent proof.** No fabricated statistics, customer names, quotes, or logos — not as placeholder realism, not as illustration. Mark the gap instead. A page carrying invented numbers is worse than useless to the person who has to publish it.

**Specify images, don't imagine them.** Diagrams and abstract work can be generated from the brief. A product screenshot, a customer logo, or a person's face cannot — those get a placeholder with a spec precise enough to act on, like `[SCREENSHOT — dashboard, campaign list, revenue column visible]`. Never fabricate a product interface: an invented screenshot is a misrepresentation the user then has to publish. Prefer showing the product over decorating the page.

**Plain verbs over category language.** Write what the product does for this buyer, in their words. "Stop guessing which campaigns drive pipeline" earns attention; "omnichannel attribution orchestration" spends it.

**Write for the committee, sell to the champion.** The primary reader has to justify this internally. Give them the argument they'll repeat to people who never saw the page — usually the finance case, the security answer, and the implementation cost.

**Concede what isn't true.** Where the category over-claims, saying so plainly buys more credibility with a senior buyer than another superlative. A page that admits a limit is trusted on the things it doesn't.

**Justify every form field.** Each visible field is defended against funnel stage in the brief. A field that can't be justified moves to follow-up or gets cut.

**Work email is always a field, and it's the floor.** B2B leads route on company domain — a personal address can't be matched to an account, enriched, or passed to sales, so the field is labelled *work email* rather than *email*. Build every form outward from that one field, adding only what the offer genuinely can't be delivered without. A form of one field is a legitimate answer; a form of six needs six justifications.

---

# Phase 2 — The build

Only after the user approves the brief.

Read `references/design-rules.md` first. It carries the constraint enforcement, the section-to-component mapping, the mobile rules, and the pre-publish checklist.

## Start by writing the build task list

Before generating any markup, create the task list for this build. It must contain these ten items, in this order, worded as tasks:

1. Inventory the assets actually available — read any connected folder and any attached files, match what's there to the brief's §8.1 and §8.2 registers, and mark those entries `real` instead of `[PLACEHOLDER]`
2. Build the sections from brief §4.1, in order, on the design system's tokens
3. Place the hero image or record the decision not to (design rules §2)
4. Render every remaining proof and image placeholder as a marked gap with its spec
5. Generate the diagrams the brief calls for
6. Build the form with the visible fields from brief §6.1 — no additions
7. **Add hidden tracking inputs: UTM source, medium, campaign, term, content, plus referrer and click ID**
8. Apply mobile rules — thumb-reach CTA, tap targets, correct input types
9. **Sweep for dead links — every `href` goes somewhere real or the link doesn't exist**
10. **Render the pre-publish checklist in full, item by item, with PASS / FAIL / N/A**

Items 7, 9 and 10 are the ones that get skipped, and they get skipped because they're invisible in a finished page — a build with no tracking fields, three dead links, and no checklist looks identical to a correct one. They are tasks, not reminders. A build that completes the visible items and not these is not finished.

Add tasks beyond these ten as the page requires. Never drop one.

## Constraints that apply throughout

- **Attention ratio 1:1.** One conversion action on the page. No navigation bar, no footer link farm, no secondary offer, no newsletter signup, no outbound links except those required for compliance.
- **The accent colour belongs to the CTA and nothing else** — including against a design system that uses it elsewhere.
- **Mobile is the primary viewport** unless the brief says otherwise.
- **Render placeholders visibly.** A missing screenshot or unproven statistic shows as a marked gap, never as invented content or a silently dropped section.

**Build wherever you are.** On a surface with a design canvas, build the page there. On a surface with file access, write the page to the working folder alongside its assets. Only if the surface can do neither should you deliver the brief plus build instructions and say where the build needs to happen.

## Finishing — task 9

**Render the pre-publish checklist from `references/design-rules.md` in full** — every item marked `PASS`, `FAIL` or `N/A`, with brief evidence, fails first. Not a summary of it. Verify against the markup actually produced rather than against what was intended; anything unverified is a fail.

Then, separately, list what the user still owes the page: unreplaced placeholders, the form endpoint, brand tokens if the build used `DEFAULT`.

The checklist and the owed-items list are different things. The first is what the build got wrong; the second is what the user has to supply. Reporting only the second reads as a clean build when it isn't one — a "key decisions" summary followed by "still owed before publish" is the owed-items list twice, with the check missing.

---

## What this skill does not do

- **Write the ads, emails, or outreach.** It asks what the visitor was promised; it doesn't write the upstream campaign.
- **Invent proof, statistics, customer names, or product screenshots.**
- **Deploy or publish.** It builds the page; publishing is the user's.
- **Write B2C or e-commerce pages.** The structure assumes a considered purchase with more than one person involved.
