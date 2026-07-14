# The Livermore Trade Gate — Go/No-Go Checklist Specification

This document formalizes the trading discipline Jesse L. Livermore describes
in *How to Trade in Stocks* (1940) **outside** the Market Key ledger itself —
Chapters I–VII ("The Challenge of Speculation" through "The Three Million
Dollar Profit"). Where RULES.md governs *what the ledger records and when a
trend has changed*, this document governs *whether a Market Key signal should
actually be acted on* — the discipline layer the book applies around its own
mechanical method.

It is implemented as the **Trade Gate**, a pure function sitting inside the
Phase 6.1 trade-policy layer (RULES.md's engine stays untouched — the gate
consumes engine *events*, it never feeds back into recording):

```ts
gate(signal, ledgerState, marketContext, positionState, gateConfig)
  → { verdict: 'GO' | 'NO_GO' | 'NEEDS_CONFIRMATION',
      items: GateItemResult[] }   // one row per checklist item, each citing its book rule
```

Same discipline as RULES.md: every item is sourced to the book with a page
citation, every vague term ("abnormal," "a limited amount") is pinned to a
deterministic rule, and every resolution is logged under
[Design Decisions](#5-design-decisions).

## 1. Why a separate document, and what it does *not* duplicate

Three of NotebookLM's proposed items are **already the Market Key itself**
and are explicitly excluded here to avoid a second, drifting copy of the same
logic:

- The "three-point confirmation" is rules 5a/5b/9a/10a/10c in RULES.md §6 —
  the pivotal-point carry-through *is* the signal, not a filter on top of it.
  Chapter V ("The Pivotal Point," book pp. 45–56) is the prose description of
  the same mechanism RULES.md formalizes from Chapters VIII–IX; the two
  chapters agree (Ch. V, p. 47: *"if the trend is going to be confirmed in a
  positive manner, it will continue to advance and reach a price over the
  Pivotal Point of 49⅝ — by 3 points or more"* — identical to rule 10a).
- The "abnormal reaction stalls near the pivot" exit is rules 10e/10f.
- Danger-signal-near-a-pivot buy/sell timing is rules 9a/9c.

What *is* genuinely new material — discipline Livermore applies **before**
and **around** a Market Key signal, not encoded in the ledger rules — is
below.

## 2. Classification

Every item is one of three kinds, and the UI must render them differently
(RULES.md §12's "manual attestation vs. computed" distinction, applied here):

| Kind | Meaning | Rendering |
|------|---------|-----------|
| **M** — Mechanical | Computable from stored data (bars, volume, position state) | Auto pass/fail, no user input |
| **A** — Attestation | Cannot be verified by software; the book requires a human judgment or discipline commitment | Checkbox the user must tick; gate blocks on it being unticked |
| **X** — Excluded | The book itself distrusts or the text is too subjective to pin down without inventing content | Not implemented; documented here so the omission is a decision, not an oversight |

## 3. Gate items

### 3a. Entry gates (apply when the Market Key emits a buy/sell-confirmation signal)

**G1 — No second commitment after a loss (M).**
*"It is foolhardy to make a second trade, if your first trade shows you a
loss. Never average losses. Let that thought be written indelibly upon your
mind."* (Ch. I, p. 20.)
Rule: if `positionState` for this instrument (or group) shows a **closed**
trade with negative net P&L within the lookback window (`noAverageLossDays`,
default 0 = "the immediately preceding closed trade," per `DD-G1`), a new
entry signal in the **same direction** is **NO_GO**. A signal in the
*opposite* direction is unaffected — this is about not doubling down on a
losing thesis, not a lifetime trading ban.

**G2 — Pyramid only into strength, never into weakness (M).**
*"Start by buying 100 shares. Then if the market advances buy another 100
shares and so on. But each succeeding purchase must be at a higher price than
the previous one... That same rule should be applied in selling short. Never
make an additional sale unless it is at a lower price than the previous
sale."* (Ch. VI, p. 58.) Reiterated at Ch. VII p. 71: after a partial
re-entry, further adds happen only "from there on," i.e., only forward, never
backward.
Rule: an **add-to-position** signal (as opposed to a fresh entry) is **GO**
only if the fill price continues in the position's direction beyond the
last fill (`newFill > lastFill` for longs, `newFill < lastFill` for shorts).
Otherwise **NO_GO** — this is a structural constraint on the position
manager, not a one-time check (§4).

**G3 — Financial safety sizing (A).**
*"Never make any trade unless you know you can do so with financial safety."*
(Ch. IV, p. 44 — closing line of the chapter.) And: *"a person engaged in the
business of speculation should risk only a limited amount of capital on any
one venture."* (Ch. IV, p. 39.)
The book never states a number — "a limited amount" is Livermore's judgment
call, not a formula (`DD-G3`). Rule: the position-sizing module (build
brief's "fixed fraction to start") computes a proposed size; the gate
displays it and requires the user to confirm **before** the first live trade
of a session — not per-trade, since re-confirming an unchanged fixed-fraction
rule every trade would be checkbox theater. Re-prompts whenever the sizing
config changes.

**G4 — No inside information (A).**
*"Beware of inside information — all inside information."* (Ch. VI, p. 67 —
Livermore instructs the reader to write this in ink on the first page of
their trading notebook.)
Rule: pure attestation, unconditional. For an automated/algorithmic tool this
reads almost as satire — the system only trades on the Market Key's own
price-derived signals by construction — but the book treats it as
foundational enough to open with, so it stays as a one-time, session-level
checkbox: *"This system trades only on price action, never on tips or
non-public information,"* satisfied by construction and simply displayed for
the human's acknowledgment, not re-asked per trade.

**G5 — Group/leadership filter (M, config-gated, off by default).**
*"Confine your studies of movements to the prominent stocks of the day. If
you cannot make money out of the leading active issues, you are not going to
make money out of the stock market as a whole."* (Ch. III, p. 33.) And:
*"it is dangerous to start spreading out all over the market... do not have
an interest in too many stocks at one time."* (Ch. III, p. 31.)
Two sub-rules, both configurable:
- **G5a (concurrency cap):** the gate is **NO_GO** for a *new* instrument if
  the count of currently open positions across all tracked instruments/groups
  already meets `maxConcurrentPositions` (default 4, echoing "today we have
  only four groups... dominating the market," Ch. III p. 33 — `DD-G5a`).
- **G5b (leadership):** for a Key Price group, a member's individual signal
  gates on group confirmation (RULES.md §12 — already implemented in the
  engine; G5b is a cross-reference, not new logic). For a standalone
  instrument, "is this a leader" has no computable proxy without a peer
  universe (relative-strength ranking against a comparison basket), which is
  real infrastructure the build brief doesn't otherwise require. **Left
  off by default** (`DD-G5b`); documented as a future config option
  (`leadershipBasket: string[]`) rather than silently ignored.

**G6 — Signal freshness (M).**
*"I never have been able to benefit much from a move if I did not get in at
somewhere near the beginning of that move."* (Ch. V, p. 45.)
Rule: a confirmation signal (rule 10a/10c) is **GO** only if it fires within
`maxSignalAgeBars` (default 3 trading days, `DD-G6`) of the pivotal point
being pierced by the confirmation margin. A late confirmation — the price
has already run well past the pivot before the policy gets to act on it — is
flagged `NEEDS_CONFIRMATION` rather than blocked outright, since the book's
concern is missing "the backlog of profit," a P&L observation, not a hard
rule; forcing a NO_GO would contradict rule 10a itself.

**G7 — Wait-and-see / signal scarcity (informational, not blocking).**
*"There are only a few times a year, possibly four or five, when you should
allow yourself to make any commitment at all."* (Ch. II, p. 26.)
This is a *description* of how rarely the Market Key should fire real signals
if the thresholds are well-tuned, not a separate rule to check per trade —
enforcing "no more than 5 trades a year" as a hard gate would fight the
engine's own signal cadence and the Phase 6.3 "ledger character" metric
already measures exactly this (column-change events per quarter). Implemented
instead as a **dashboard statistic** ("signals this year: N") with a
soft warning if N is trending far above the book's cadence — visibility, not
a blocker (`DD-G7`).

### 3b. Exit gates (apply continuously while a position is open)

**G8 — Intraday abnormal-break exit (M).**
*"By 'abnormal' I mean a reaction in one day of six or more points from an
extreme price made in that same day... when something happens abnormally
stock-marketwise, it is flashing you a danger signal which must not be
ignored."* (Ch. II, p. 23.)
This is **distinct** from RULES.md rules 10e/10f (a multi-day failure to
carry through a *pivotal point*) — G8 is a single-bar, intraday-range check
against that bar's *own* high, independent of any pivotal point. Rule: for an
open long, if `(bar.high - bar.low) / bar.high ≥ abnormalBreakThreshold`
**and** `bar.close` is in the lower half of that range, emit `NO_GO` (exit).
Threshold: `swing threshold` value for the instrument (percent mode) or the
book's literal 6 points (absolute/book mode) — reusing the Market Key's own
threshold keeps one number to tune, not two (`DD-G8`). Mirrored for shorts.

**G9 — Margin call / hard-stop breach (M).**
*"I know but one sure tip from a broker. It is your margin call. When it
reaches you, close your account. You are on the wrong side of the market."*
(Ch. IV, p. 38.)
There is no broker or margin in a paper-trading/backtest context, so this is
reinterpreted as the **hard stop-loss** implied by G3's sizing decision: if
open unrealized loss on a position reaches the pre-committed risk amount from
G3, exit unconditionally, no override (`DD-G9`). This is the one gate item
that, once armed, cannot be dismissed by the user for that position — it *is*
the financial-safety commitment being honored.

**G10 — Staleness (M).**
Synthesized from *"Don't let the stock go stale on you... don't let patience
create a frame of mind that ignores the danger signals"* (Ch. II, p. 22) and
the pivotal-point non-performance warning (Ch. V, p. 51: *"if the stock does
not perform as it should, after crossing the Pivotal Point, this is a danger
signal"*). The book names the *symptom* ("stale") without a number — pinned
here as: the position's instrument has recorded **no new extreme in the
trend column** for `staleDays` (default 10 trading days, roughly two book
weeks — `DD-G10`) → flag `NEEDS_CONFIRMATION` (a prompt to review, not an
automatic exit, since "stale" in the book is a call to attention, not itself
rules 10b/10d's over-signal).

### 3c. Excluded (X) — the book's own reasoning why

**The "inner mind tip-off."** *"Frankly, I am always suspicious of the inner
mind tip-off and usually prefer to apply the cold scientific formula."*
(Ch. VI, p. 66.) Livermore describes a genuine phenomenon (a trader's
subconscious unease before a reversal) but explicitly does not trust it over
his mechanical records, and offers no observable proxy for it. NotebookLM's
suggestion to model it as "extreme volatility" is not supported by the text —
volatility is already G8/G10's job. **Not implemented**; noted so the
omission reads as a decision.

**"Testing orders" in a related market** (Ch. VII, pp. 73–74 — the Rye
probe before committing to Wheat). Genuinely mechanizable in principle (place
a small order in a correlated instrument and read the market's response
before sizing the primary position), but it is a bespoke, single-instance
tactic even in the book ("I decided... to test my theory") and would require
a second correlated-market data feed with no general rule to pin. **Left as
a documented future idea**, not a Phase 6.1 gate item.

## 4. Position-manager integration (G2, G9)

G2 and G9 aren't stateless per-signal checks — they need to read and write
the same position state Phase 5b's paper-trading tracker already maintains
(entry price, direction, fills, unrealized P&L). No new state store: the
gate takes `positionState` as a parameter, exactly like the engine takes
`LedgerState`, keeping the gate as I/O-free as the rule engine itself
(RULES.md's "zero I/O" principle applies here too — the gate is called with
data already fetched, never fetches on its own).

## 5. Design Decisions

Numbering continues informally from RULES.md's DD-n but uses a `DD-Gn` prefix
to keep the two documents' decision logs independently auditable.

| ID | Question | Resolution | Rationale |
|----|----------|------------|-----------|
| DD-G1 | "Never make a second trade if the first shows a loss" — for how long, and against the whole instrument or just that thesis? | Applies to the immediately preceding **closed** trade on the same instrument, same direction, no time decay by default (`noAverageLossDays: 0`) | The book gives no window; a same-direction re-entry right after a loss is exactly "averaging losses" in spirit even without literally adding to an *open* position. |
| DD-G3 | "A limited amount of capital" — no number given | Delegated entirely to the existing Phase 6.1 position-sizing config (fixed fraction); G3 is a confirmation gate on that number, not a new number | The book explicitly declines to give a formula; inventing one here would misattribute a number to Livermore. |
| DD-G5a | "Four groups... dominating the market" as a concurrency cap | `maxConcurrentPositions` default 4, configurable | Explicit number in the text (Ch. III), reused as a sane default rather than a hardcoded rule — the book itself notes leadership rotates ("the leaders of today may not be the leaders two years from now"). |
| DD-G5b | Can "leadership" be computed for a standalone (non-grouped) instrument? | No general proxy without a peer-comparison basket; left off by default, config hook reserved | Avoids fabricating a leadership metric the book doesn't define outside the two-stock Key Price comparison RULES.md §12 already covers. |
| DD-G6 | "Near the beginning of the move" — how near? | 3 trading days from confirmation, downgrades to a warning (`NEEDS_CONFIRMATION`) rather than a block past that | Directional guidance from the book, not a hard number; blocking outright would contradict the confirmation signal itself. |
| DD-G7 | "Four or five times a year" as a per-instrument trade cap? | Not a gate; surfaced as a dashboard statistic instead, cross-referenced to the Phase 6.3 ledger-character metric | A hard cap here would fight the engine's own signal cadence rather than validate it; Phase 6.3 already measures this empirically per threshold setting. |
| DD-G8 | "Six or more points" — percent or absolute, and which threshold? | Reuses the instrument's existing Market Key swing threshold (not a new second number) | One threshold to tune per instrument beats two; the book's "six points" is literally the same swing basis used elsewhere (RULES.md §1). |
| DD-G9 | No margin call exists outside a real broker relationship | Reinterpreted as an unconditional hard-stop at the G3-committed risk amount | Preserves the *function* of Livermore's "one sure tip" (a forced, undebatable exit) without inventing a fictional margin mechanic. |
| DD-G10 | "Stale" — no definition given | 10 trading days without a new trend-column extreme; downgrades to a review prompt, not an auto-exit | The book's own usage is a call to attention ("don't let patience... ignore the danger signals"), not a rule with the force of 10b/10d. |

## 6. Book rule index → gate item cross-reference

| Book location | Gate item(s) |
|----------------|--------------|
| Ch. I, "Never average losses" (p. 20) | G1 |
| Ch. II, volume/normal-reaction description (pp. 21–22) | *(informational only — no gate; volume data storage is a Phase 4 data-layer note, not a checklist item, since the book's volume guidance is descriptive of what a *healthy* trend looks like, not a separate pass/fail test beyond G8)* |
| Ch. II, abnormal one-day break (p. 23) | G8 |
| Ch. II, "four or five times a year" (p. 26) | G7 |
| Ch. III, leaders / no spreading out (pp. 31–33) | G5a, G5b |
| Ch. IV, "risk a limited amount" / "financial safety" (pp. 39, 44) | G3 |
| Ch. IV, margin call (p. 38) | G9 |
| Ch. IV, reserve fund (pp. 40–43) | *(portfolio-level policy, not a per-trade gate — see §7)* |
| Ch. V, Pivotal Point mechanism (pp. 45–56) | Already RULES.md §6 (rules 5, 8, 9, 10); G6 (freshness) is the one net-new item |
| Ch. VI, pyramiding rule (p. 58) | G2 |
| Ch. VI, "beware of inside information" (p. 67) | G4 |
| Ch. VI, inner mind tip-off (p. 66) | Excluded (§3c) |
| Ch. VII, testing orders (pp. 73–74) | Excluded, documented as future idea (§3c) |

## 7. Note: the reserve-fund rule is not a Trade Gate item

The book states the reserve-fund discipline **twice**, with two different
triggers: *"a speculator should make it a rule each time he closes out a
successful deal to take one-half of his profits and lock this sum up in a
safe deposit box"* (Ch. IV, p. 40) versus *"when a speculator is fortunate
enough to double his original capital he should at once draw out one-half of
his profit... for reserve"* (Ch. IV, pp. 42–43). Both are **capital
withdrawal policy**, not a condition on whether to enter or exit a trade —
they belong in the Phase 5b paper-trading dashboard as a portfolio-level
statistic ("reserve-eligible profit: $X, per per-deal / per-doubling rule")
rather than the Trade Gate. Noted here so the two book passages aren't lost,
and flagged for the Phase 5b spec rather than implemented as a gate item.
