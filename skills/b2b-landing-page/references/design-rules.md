# Design rules

Read this before building (Phase 2). It carries the constraints the build enforces, the map from section type to component, the hero-image decision, the mobile rules, and the pre-publish checklist rendered at finish.

The build task list in `SKILL.md` is the order of operations. This file is the *how* for each step, and the checklist in §6 is the gate the build passes through before it's called finished.

---

## §1 — Constraints that hold throughout

These are not preferences. A page that breaks one of them is broken in a way that looks identical to a correct page, which is exactly why they're enforced rather than trusted.

- **Attention ratio 1:1.** Exactly one conversion action on the page. No navigation bar, no footer link farm, no secondary offer, no newsletter signup, no outbound links except those required for compliance. Every additional thing a visitor can do divides the attention the one action needed.
- **One CTA wording.** The conversion action's text (brief §2.1) is identical everywhere it appears. Varying it for rhythm reads as craft and behaves as three different offers.
- **The accent colour belongs to the CTA and nothing else** — including against a design system that uses it elsewhere. If the CTA can't win contrast against its background, change the CTA's colour, not the rule.
- **Mobile is the primary viewport** unless the brief says otherwise. Design the fold, the form, and the CTA for a thumb first (§4).
- **Render placeholders visibly.** A missing screenshot or an unproven statistic shows as a marked gap — `[SCREENSHOT — …]`, `[PROOF NEEDED — …]` — never as invented content and never as a silently dropped section.
- **Never invent proof or product UI.** No fabricated statistics, customer names, quotes, logos, or screenshots of an interface that doesn't exist. The gap is the honest deliverable.

---

## §2 — Hero image placement

The hero either shows the product or earns its keep some other way. Decide explicitly and record the decision — "no hero image, and here's why" is a valid, logged outcome, not an omission.

**Place a hero image when** there is a `real` product screenshot in brief §8.2, or a diagram that can be generated from the brief and makes the fold's one thing (brief §4.2) clearer. Showing the product beats decorating the fold.

**Record the decision not to place one when** the only available option would be a fabricated interface, generic stock, or decoration that competes with the headline for the fold. A clean type-led hero outperforms a fake screenshot every time. Write the decision down so it reads as a choice, not an accident.

**Never fabricate the interface.** If the product shot doesn't exist, the fold carries the `[SCREENSHOT — spec]` placeholder from §8.2 — it does not carry an invented UI. An invented screenshot is a misrepresentation the user then has to publish.

Whatever is placed serves brief §4.2. An image that doesn't advance the fold's one thing is decoration, and decoration in the hero costs conversions.

---

## §3 — Section-to-component mapping

Build each section type from brief §4.1 as the component below. Only these types exist; a page reaching for something outside the set is usually trying to do two jobs.

| Section type | Component | Notes |
|---|---|---|
| `hero` | Headline + subhead + primary CTA (+ optional hero visual per §2) | Keeps the inbound promise. Carries the fold's one thing. |
| `proof-bar` | Row of logos / rating / a single hard metric | Every entry a `real` §8.1 asset or a marked gap — never a placeholder logo. |
| `problem` | Short framing block, buyer's own words | Full length on cold, one line on warm, omitted on bottom. |
| `solution` | The mechanism — what the product does, plainly | Lead with this on warm traffic. |
| `how-it-works` | 3–4 step sequence or a generated diagram | Diagram is generatable (§8.2 `generate`); a UI screenshot inside it is not. |
| `outcome` | The after-state, tied to a §8.1 proof element | No claim without adjacent proof or a marked gap. |
| `objection` | Question-and-answer or concession block | Survives at every stage. Bottom-funnel objections are more specific, not fewer. |
| `proof-detail` | Case study, named quote, or metric with context | Pulls from §8.1; absent proof shows as `[PROOF NEEDED — …]`. |
| `final-cta` | Restated CTA, identical wording, with the form or its trigger | Same accent, same words as every other CTA instance. |

**Claims and proof travel together.** Every claim in a section either sits beside a §8.1 proof element or carries a visible `[PROOF NEEDED — describe what would prove this]` marker inline. Proof quarantined in a bottom-of-page logo bar isn't proof of anything specific.

**A design system supplies the tokens; a template supplies structure you mostly strip.** Keep a template's typography, spacing, and component styling — remove its nav, footer links, secondary CTAs, and any off-vocabulary section, then rebuild the order from §4.1. Tell the user what was stripped and why ("removed to hold the attention ratio at 1:1").

---

## §4 — Mobile rules

Mobile is the primary viewport. Verify each of these against the markup, not the intent:

- **CTA within thumb reach.** The primary action sits in the lower-middle of the fold on a phone, not stranded top-right where a desktop nav would put it.
- **Tap targets at least 44×44px**, with spacing so adjacent targets aren't mis-tapped.
- **Correct input types on every field.** `type="email"` for work email (brings up the right keyboard and enables validation), `type="tel"` for phone, appropriate `inputmode` for numeric fields. A wrong input type is a conversion tax paid on every mobile submit.
- **No horizontal scroll.** Content, tables, and images stay within the viewport; wide elements wrap or scroll inside their own container, never the page body.
- **The fold holds the one thing on a phone.** Headline, subhead, and CTA are visible without scrolling on a common phone height — not pushed below by an oversized hero image.

---

## §5 — Hidden tracking fields

The form carries these invisible inputs (brief §6.2), added at build time and never shown to the visitor:

`utm_source` · `utm_medium` · `utm_campaign` · `utm_term` · `utm_content` · `referrer` · click ID (`gclid` / `fbclid` / equivalent)

They read from the query string on load and submit with the form. They're attribution, not data collection — they never count against the form's visible length (§6.1). Their absence is invisible in a finished page, so the build treats adding them as a task, not a reminder.

---

## §6 — Pre-publish checklist

Render this **in full** at finish — every item marked `PASS`, `FAIL`, or `N/A`, with one line of evidence, **fails first**. Verify each against the markup actually produced, not against what was intended; anything you can't verify is a `FAIL`, not an omission. This is not a summary and not the owed-items list — it is what the build got right or wrong.

| # | Check | Verify against |
|---|---|---|
| 1 | Attention ratio is 1:1 — one conversion action, no nav, no footer links, no secondary offer | Count every clickable path off the page |
| 2 | CTA wording is identical at every instance and matches brief §2.1 | Diff every CTA string |
| 3 | Accent colour is used only for the CTA | Search the styles for the accent value |
| 4 | Hero keeps the inbound promise for the traffic source (brief §2.2 / §2.5) | Compare hero to the promise the visitor arrived on |
| 5 | Every claim has adjacent proof (§8.1) or a visible `[PROOF NEEDED — …]` marker | Walk each claim in §4.1 |
| 6 | No invented proof — no fabricated stat, name, quote, logo, or screenshot | Check each §8.1 / §8.2 entry is `real` or marked |
| 7 | No fabricated product interface; missing screenshots show as `[SCREENSHOT — spec]` | Inspect every product visual |
| 8 | Work email is present and labelled *work email*; every other visible field is justified (§6.1) | Read the form fields and their justifications |
| 9 | Hidden tracking fields present — UTM ×5, referrer, click ID (§5) | Inspect the form's hidden inputs |
| 10 | Section order matches brief §4.1 and the stage rules; objection handling present | Compare rendered order to the brief |
| 11 | Mobile rules applied — thumb-reach CTA, 44px targets, correct input types, no horizontal scroll (§4) | Check at a phone viewport |
| 12 | No dead links — every `href` resolves somewhere real, or the link doesn't exist | Follow every `href` |
| 13 | Placeholders render visibly; no section silently dropped for a missing asset | Scan for marked gaps vs. empty spots |
| 14 | Brand tokens sourced per §7.5; `DEFAULT` flagged if used | Check the token source |

After the checklist, and **separately**, list what the user still owes the page: unreplaced placeholders, the form endpoint, and brand tokens if the build used `DEFAULT`. The checklist is what the build got wrong; the owed-items list is what the user has to supply. Reporting only the second reads as a clean build when it isn't one.
