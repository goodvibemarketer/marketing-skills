# Brief schema

Read this before writing the brief (Phase 1, step 5). It is the full field list for `brief-<product-slug>-<page-slug>.md`, and for every field it says what to do when the answer is missing.

The rule that runs through all of it: **a missing field is inferred and logged, never left blank and never invented.** Anything you inferred goes in the assumption log (§1.2) so the user can correct it. The two things you may never infer are proof (§8.1) and product screenshots (§8.2) — those become marked gaps instead.

Use the section numbers below verbatim. Other files point at them — the build reads §4.1 and §6.1, the design-system path writes §7.5, the asset inventory marks §8.1 and §8.2, and §2.5 catches unknown traffic.

---

## §1 — Objective

### §1.1 Page objective
The business outcome the page exists to produce, in one line. Not "get leads" — *"book qualified demos with RevOps leaders at 200+ headcount SaaS companies."* This is one of the three stops; it is asked, never inferred.

**Missing:** stop and ask. Without it there is no page — everything downstream is a guess about what "working" means.

### §1.2 Assumption log
Every field that was inferred rather than given, most-likely-wrong first. This opens the delivered brief. One line each: what was assumed and what it rests on. A short honest list beats a confident brief built on an unseen wrong premise.

**Missing:** if nothing was inferred, say so explicitly — "no assumptions, everything here was supplied." An absent log reads as "nothing was guessed," which is rarely true.

---

## §2 — Traffic and conversion

### §2.1 Conversion action
The single thing a visitor can do, in the exact words that appear on the button. *"Get my free audit,"* not "audit request flow." This wording is reused unchanged everywhere the CTA appears (see the copy rules). It is a stop; it is asked.

**Missing:** stop and ask. Do not infer the CTA — the whole page is built to drive this one action, and inventing it means building toward the wrong outcome.

### §2.2 Traffic source
Where visitors arrive from: a named paid channel, an email, organic search, a sales conversation, or `mixed-unknown`. It sets what the hero must keep faith with (the inbound promise).

**Missing:** if the user genuinely can't say, record `mixed-unknown` and apply §2.5.

### §2.3 Funnel stage
How much the visitor already knows, as one of `cold` · `warm` · `bottom`. This drives section order and page length.

| Stage | What it means | Structure it forces |
|---|---|---|
| **Cold** | No prior relationship; arrived from an interruption (cold ad, list buy). | Problem framing before any offer. Longest page. Proof early — trust starts at zero. |
| **Warm** | Knows the category and roughly who you are (retargeting, nurtured email). | Problem compressed to a line. Lead with the mechanism. |
| **Bottom** | Actively evaluating; high intent (branded search, "book a demo" click). | Shortest path to the form. Problem framing omitted. Objection handling stays. |

**Missing:** infer from the traffic source (§2.2) and log it — retargeting reads warm, branded search reads bottom, a cold list reads cold. If the source is `mixed-unknown`, default to `cold` and say why: a page that assumes no prior context is safe everywhere, just not optimal anywhere.

### §2.4 Friction decision
Recorded only when the ask (§2.1) is large relative to how warm the traffic (§2.3) is — a live audit from a cold click, a demo from a first-time visitor. Resolve it as one of:
- **earn it** — more proof and objection handling before the form;
- **reduce it** — lower the ask;
- **split it** — a smaller first step that qualifies into the real one.

State which and why.

**Missing / not applicable:** if ask and warmth are matched, write "no friction gap." Never silently leave a heavy ask on cold traffic unaddressed.

### §2.5 When the traffic source is unknown
Applies whenever §2.2 is `mixed-unknown`. A page that can't assume prior context is weaker than a matched one — build it, but don't imply otherwise.

- Treat the stage as `cold` (§2.3) unless the user says otherwise.
- Write a hero that keeps a promise broad enough to hold across every plausible source, rather than one tuned to a channel you can't confirm.
- Log this as an assumption in §1.2 and say plainly, in the delivered brief, that a matched page would convert better — offer to build per-source variants once the sources are known.

Do not paper over the gap with a hero that quietly assumes one channel. Naming the weakness is the honest move; hiding it produces a page that underperforms for reasons the user can't see.

---

## §3 — Product and market

### §3.1 Product in one sentence
What it does, for this buyer, in their words — not the category label. This is asked in beat one if the user hasn't already given it.

**Missing:** stop and ask. Nothing else in the brief is inferable until the product is known; this is the pivot the two-beat questioning turns on.

### §3.2 Category and how it's named
The category the buyer would put this in, and the language they actually use for it. Feeds the "plain verbs over category language" copy rule.

**Missing:** infer from §3.1 and log it.

### §3.3 The real alternative
What the buyer does *instead* today — usually a spreadsheet, a manual process, an incumbent tool, or nothing. This is the thing the page competes against, and it's rarely a direct competitor.

**Missing:** infer and present as a correctable draft in beat two (*"Real alternative: a spreadsheet someone in ops maintains by hand"*). Log it in §1.2.

---

## §4 — Message and structure

### §4.1 Section-by-section copy
The ordered spine of the page and the copy for each section. **This is what the build consumes** — it builds sections from here, in this order. Each entry carries:

- **type** — one of the fixed vocabulary: `hero` · `proof-bar` · `problem` · `solution` · `how-it-works` · `outcome` · `objection` · `proof-detail` · `final-cta`. Sections may repeat or be omitted; nothing outside the set.
- **copy** — headline, subhead, body, and CTA text where the section carries one. CTA wording is identical to §2.1 every time it appears.
- **proof refs** — for any claim, the §8.1 register entry that backs it, or a `[PROOF NEEDED — describe what would prove this]` marker.
- **image refs** — the §8.2 register entry, or a placeholder spec precise enough to act on.

Order follows the stage rules in §2.3. Objection handling (`objection`) survives at every stage — a buyer close to converting has more specific objections, not fewer.

**Missing:** this is authored, not supplied. It can't be "missing" — but any section whose copy depends on an unproven claim or an absent screenshot carries the marker inline rather than being dropped or faked.

### §4.2 The one thing above the fold
A single sentence naming what the fold must land. If it takes two sentences, it isn't one thing yet — narrow it. Everything in the `hero` serves this.

**Missing:** derive from §1.1 and §2.1 — the fold exists to make the conversion action feel worth taking. Log the derivation.

### §4.3 Section-order reasoning
One line per structural choice: why this order, and any deviation from the stage default stated openly rather than made silently.

**Missing:** if the order is the plain stage default, say "standard <stage> order, no deviations."

---

## §5 — Audience

### §5.1 Primary buyer and what they're accountable for
The champion — the person the page speaks to — and the number or outcome they own internally. The page hands them the argument they'll repeat to people who never saw it.

**Missing:** infer from the product and objective, present as a correctable draft in beat two, log in §1.2.

### §5.2 Buying committee
Who else has to say yes, and what each one weighs — typically a finance case, a security answer, an implementation-cost answer. *"Head of Security champions, CTO and Legal evaluate."*

**Missing:** infer the committee shape from the category and deal size; log it. B2B is a considered purchase — assume more than one reader unless told otherwise.

### §5.3 Pain
The specific, present pain the buyer feels — concrete and dated, not a category ache. *"A customer is demanding a certificate before they'll sign."*

**Missing:** infer and present as a correctable draft. Being wrong here costs the user one corrected line; a blank textarea labelled "what's the biggest pain your buyer feels?" costs them the time they came to save.

### §5.4 Objections
The two or three reasons this buyer stalls, including the one the page most has to beat — often *"we'll build this in-house"* or *"now isn't the time."* Each maps to an `objection` section or a concession (§7.3).

**Missing:** infer from the alternative (§3.3) and committee (§5.2); log. The in-house-build and do-nothing objections are safe defaults for most B2B tools.

---

## §6 — Form

### §6.1 Visible form fields
The exact fields the visitor sees, each defended against funnel stage. Build outward from the floor — a field earns its place or it's cut.

- **Work email is always present and always the floor.** Labelled *work email*, not *email*: B2B leads route on company domain, and a personal address can't be matched to an account, enriched, or passed to sales. A one-field form is legitimate. A six-field form needs six justifications.
- Add a field only when the offer genuinely can't be delivered without it. Record the justification beside each: *"company — the audit is company-specific; monthly spend band — to scope it."*
- A field that can't be justified moves to a follow-up step or gets cut.

**Missing:** default to work email alone and note that anything else is addable once the offer's delivery needs are known. Never add speculative fields for "richer" leads — a longer form asked of a senior buyer costs more conversions than the extra data is worth.

### §6.2 Hidden fields
The tracking inputs the form carries invisibly, added at build time: UTM source, medium, campaign, term, content, plus referrer and click ID. These are attribution, not data collection — they never appear to the visitor and never count against the form's length.

**Missing:** always present. Their absence is invisible in a finished page, which is exactly why the build treats them as a task, not a reminder.

---

## §7 — Brand and tone

### §7.1 Tone of voice
How the page should sound to this buyer — usually a register, not an adjective list. Senior B2B buyers trust plain and specific over energetic and superlative.

**Missing:** infer from audience (§5) and log — default to plain, direct, concession-friendly.

### §7.2 Words to use and avoid
The buyer's own terms to reach for, and the category jargon to drop. Feeds the "plain verbs over category language" rule.

**Missing:** infer from §3.2; log.

### §7.3 Concessions
Where the category over-claims, the limit this page admits plainly. Conceding what isn't true buys credibility with a senior buyer on the things the page *does* claim.

**Missing:** optional but valuable. If none is offered, note that a concession would strengthen the page and suggest one.

### §7.4 Design system or template in play
Whether the surface supplied a design system, a template, both, or neither — and what that means for §7.5. A design system supplies brand tokens (skip §7.5's questions). A template supplies structure, most of which is stripped (nav, footer links, secondary CTAs, off-vocabulary sections) before the section order is rebuilt from §4.1.

**Missing:** record "neither" and run the §7.5 cascade.

### §7.5 Brand token cascade
The source of colours, typography, and component styling, resolved in this order and recorded here:

1. **Design system supplied** → record the system as the source. Skip the token questions. One check survives: the CTA needs clear contrast against its background; if the system's palette can't give it, use an accent that can and record the deviation.
2. **User-supplied tokens** → ask for colours and fonts; record them.
3. **Website URL** → pull tokens from the user's existing site; record the source.
4. **`DEFAULT`** → a neutral, restyleable default the user can change in one instruction. Record `DEFAULT` explicitly so the owed-items list flags it.

The accent colour is reserved for the conversion action and nothing else — including against a design system that uses it elsewhere.

**Missing:** fall through the cascade to `DEFAULT` and log it as owed.

---

## §8 — Asset registers

Two registers of what the page needs to show. Before assuming anything is absent, read any connected folder and any attached files — logos, screenshots, case studies, and brand guidelines are often already there, and asking for what's been supplied looks careless. Entries the build confirms on disk are marked `real`; everything else is a marked gap with a spec.

### §8.1 Proof asset register
Every proof element the copy leans on: customer logos, named quotes, case studies, metrics, certifications, third-party ratings. For each: what it is, whether it exists `today`, and the §4.1 claim it backs.

- **Ask, don't infer, and ask for what exists right now.** Proof is the one thing inventing which is the failure the whole brief guards against. Frame the question around what's in the user's hands today, and make "nothing yet" an easy, unembarrassing answer.
- **Never invent proof** — no fabricated statistics, customer names, quotes, or logos, not even as placeholder realism.
- Anything absent becomes `[PROOF NEEDED — describe what would prove this]` in §4.1, not an invented stand-in. If something claimed to exist later turns out not to, it reverts to a placeholder.

**Missing:** an empty register is normal for an early-stage product. Record it honestly; the page ships with visible gaps rather than fabricated evidence.

### §8.2 Image and visual asset register
Every visual the page places: product screenshots, hero imagery, customer faces, diagrams. For each: what it is, whether it exists `today`, and whether it can be generated.

- **Diagrams and abstract visuals** can be generated from the brief — mark them `generate`.
- **Product screenshots, customer logos, and real faces cannot be generated.** They get a placeholder with a spec precise enough to act on — `[SCREENSHOT — dashboard, campaign list, revenue column visible]`. **Never fabricate a product interface**; an invented screenshot is a misrepresentation the user then has to publish.
- Prefer showing the product over decorating the page.

**Missing:** record the gap with its spec. A marked `[SCREENSHOT — …]` placeholder is the deliverable, never a generated fake of the real UI.
