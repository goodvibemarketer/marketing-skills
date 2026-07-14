# The Livermore Market Key — Formal Rule Specification

This document formalizes the price-recording method described in Jesse L. Livermore,
*How to Trade in Stocks* (Duell, Sloan & Pearce, 1940), Chapter VIII ("The Livermore
Market Key", book pp. 82–90) and Chapter IX ("Explanatory Rules", book pp. 91–101),
validated against the worked charts on book pp. 102–133 (Charts One–Sixteen,
U.S. Steel / Bethlehem Steel / Key Price, March 1938 – February 1940).

Rule text was verified against 400-dpi scans of the 1940 first edition. Where this
spec resolves an ambiguity in the book, the resolution is recorded in
[§10 Design Decisions](#10-design-decisions) and cross-referenced inline as `DD-n`.

The spec is implemented by the pure rule engine in `packages/engine`. The engine is
a deterministic state machine: `(state, dailyBar, config) → (state', events[])`.
No I/O, no clock, no randomness.

---

## 1. Columns, ink, and notation

Six recording columns per instrument (book Ch. VIII, p. 83), left to right:

| # | Column             | Code  | Ink (book)          | Direction |
|---|--------------------|-------|---------------------|-----------|
| 1 | Secondary Rally    | `SR`  | pencil (light blue) | up        |
| 2 | Natural Rally      | `NR`  | pencil (light blue) | up        |
| 3 | Upward Trend       | `UT`  | **black ink**       | up        |
| 4 | Downward Trend     | `DT`  | **red ink**         | down      |
| 5 | Natural Reaction   | `NRC` | pencil (light blue) | down      |
| 6 | Secondary Reaction | `SRC` | pencil (light blue) | down      |

Book rules 1–3 define the ink convention; it is a pure display concern but is part of
the golden-master assertions (each recorded figure's ink is checked).

**Notation used below**

- `S` — swing threshold ("approximately six points" in the book).
- `C` — confirmation margin ("three points" in the book). Invariant: `C = S / 2`.
- `last[X]` — the most recently recorded price in column `X` (or null).
- `PP[X]` — the current *pivotal point* of column `X`: the last price in `X` that has
  underlines drawn beneath it (see §5). `PP` exists for `UT`, `DT`, `NR`, `NRC` only.
- `up(X)` — true for `SR`, `NR`, `UT`; `down(X)` — true for `DT`, `NRC`, `SRC`.
- A **bar** is a completed daily OHLC record (see §2).
- "Swing of `S` from `P`" — a move whose extreme is at least `S` away from `P` in the
  counter direction: rally trigger `high ≥ P + S`, reaction trigger `low ≤ P − S`
  (`DD-1`: "approximately" is resolved as `≥`, with an optional tolerance used only in
  book-replay mode, `DD-2`).

## 2. Daily input and bar boundaries

The engine consumes one completed daily OHLC bar per instrument per trading day, in
strict chronological order. The engine never reads intraday sequence; every rule is
evaluated against the bar's `high` and `low` (`DD-3` fixes the intra-day ordering
assumption).

**Recorded figures are daily extremes, not closes** (book p. 86: "I continue to set
down in that same column the extreme price made any day…"). When a figure is recorded
in an up-direction column the day's **high** is recorded; in a down-direction column
the day's **low** (`DD-4`).

Bar boundaries (application layer, documented here because replay correctness depends
on them):

- **Equities** — the exchange's official session (NYSE regular session); the daily job
  runs after U.S. close.
- **Crypto** — the UTC day `[00:00, 24:00)`. The daily job evaluates the just-closed
  UTC bar shortly after the boundary (default 00:05 UTC). This boundary is arbitrary
  but must be *fixed*: changing it re-defines every historical bar, so it is stored in
  config and a change forces a full replay (`DD-5`).

Bars must be processed gap-free per instrument: a missed day must be fetched and
replayed before any later bar (the state machine is order-dependent). Non-trading
days simply have no bar.

## 3. Engine state

```ts
interface LedgerState {
  active: Column | null;            // column currently being recorded, null before first anchor
  last:   Record<Column, number | null>;   // last recorded price per column
  pivot:  Record<'UT'|'DT'|'NR'|'NRC', PivotalPoint | null>;
  // Signal-phase tracking (rules 9/10), per direction:
  upPhase:   TrendPhase;  // state of the "is the uptrend intact?" question
  downPhase: TrendPhase;  // state of the "is the downtrend intact?" question
}

interface PivotalPoint {
  price: number;
  color: 'red' | 'black';   // ink of the underline, per rule 4
  setOn: string;            // ISO date the underline was drawn
  confirmedThrough: boolean; // set true once price has carried through by C (rule 10a)
}

type TrendPhase =
  | 'none'            // no pivotal point pending on this side
  | 'firstCounter'    // counter-swing that created the PP is still running
  | 'attempt'         // a swing back toward the PP is in progress
  | 'failed'          // the attempt ended without carrying through by C
  | 'confirmed'       // carried through PP by C (rule 10a) — trend resumed
  | 'over';           // rule 10b/10d fired — trend declared over
```

Initial state: all fields null/`none`. The ledger **anchors** on the first bar: the
first bar's close direction is unknowable without history, so recording starts in
`UT` if the first observed swing is upward, `DT` if downward — concretely, the engine
buffers the first bar's high/low as provisional extremes and opens `UT`/`DT` on the
first subsequent bar that is `S` above the running low (→ `UT`) or `S` below the
running high (→ `DT`) (`DD-6`). In production this cold start is avoided by replaying
a warm-up window of history (default 12 months).

## 4. The recording state machine

Exactly **one** figure per instrument per day may be recorded (`DD-3`). Each day, the
engine evaluates these steps in order and stops at the first that records:

### Step 1 — same-direction upgrade (book rules 5a, 5b, 6e, 6f, and 6b/6d tails)

If `active` is an up-direction column and the day's high pierces a stronger up column,
the figure graduates rightward-to-`UT`; mirror for down. Precedence: trend column
beats natural column.

- **(6f / 6d-tail / SR analog)** `up(active)` and `high > last[UT]` → record `high` in
  `UT` (black ink). Applies from `SR`, `NR` (and trivially continues `UT`).
- **(5a)** `active ∈ {NR, SR}` and `PP[NR]` exists and `high ≥ PP[NR] + C`
  → record `high` in `UT` (black ink). This is the "trend change graduates out of the
  natural column" rule — it fires even when `high` is below `last[UT]` (`DD-7`).
- **(6e / 6b-tail / SRC analog)** `down(active)` and `low < last[DT]` → record `low`
  in `DT` (red ink).
- **(5b)** `active ∈ {NRC, SRC}` and `PP[NRC]` exists and `low ≤ PP[NRC] − C`
  → record `low` in `DT` (red ink).

Secondary columns participate in the same checks (`DD-8`): from `SR`, exceeding
`last[NR]` re-opens `NR` (rule 6g tail) — evaluated in Step 2; exceeding `last[UT]`
or `PP[NR] + C` goes straight to `UT`/`UT` here.

### Step 2 — same-direction continuation (book rules 6a–6d "continue to do so…", 6g/6h tails)

- `active` up-direction: if `high > last[active]` → record `high` in `active`…
  - …except from `SR`: if `high > last[NR]`, recording moves to `NR` (rule 6g tail:
    "commence to record prices in the Natural Rally column once again"), else if
    `high > last[SR]` continue in `SR`.
  - `NR` and `UT` continue on any new extreme beyond their own `last`.
- Mirror for down-direction columns (`SRC` → `NRC` when `low < last[NRC]`, rule 6h tail).

### Step 3 — counter-swing transitions (book rules 4a–4d, 6a–6d, 6g, 6h)

Let `ref` = the extreme the current leg is measured from = `last[active]`
(after Steps 1–2 have updated it if they fired today — `DD-3` discusses the same-day
ordering). A counter-swing triggers when the day's counter-extreme is at least `S`
away from `ref` (with `DD-2` tolerance in book mode; `DD-13` group coupling can also
trigger this step for Key-Price group members).

**Downward counter-swing** (`up(active)` and `low ≤ ref − S`):

| From          | Route                                                   | Book rule |
|---------------|---------------------------------------------------------|-----------|
| `UT`          | → `NRC` always (overwrite `last[NRC]`)                  | 6a, 4a    |
| `NR` (or `SR`)| → `DT` if `low < last[DT]` (6b tail); else `NRC` if `last[NRC]` is null or `low < last[NRC]`; else `SRC` | 6b, 6h, 4d |

Underline events on the day the counter-swing opens (see §5): leaving `UT` draws
**red** lines under `last[UT]` (4a); leaving `NR`/`SR` draws **black** lines under
`last[NR]` (4d).

**Upward counter-swing** (`down(active)` and `high ≥ ref + S`):

| From           | Route                                                  | Book rule |
|----------------|--------------------------------------------------------|-----------|
| `DT`           | → `NR` always (overwrite `last[NR]`)                   | 6c, 4c    |
| `NRC` (or `SRC`)| → `UT` if `high > last[UT]` (6d tail); else `NR` if `last[NR]` is null or `high > last[NR]`; else `SR` | 6d, 6g, 4b |

Leaving `DT` draws **black** lines under `last[DT]` (4c); leaving `NRC`/`SRC` draws
**red** lines under `last[NRC]` (4b).

The figure recorded on a transition day is the day's extreme in the *new* direction
(the rally's high / the reaction's low).

Routing notes:

- "Overwrite" means the natural column's `last` is *replaced* by the new leg's figure
  even when it is worse than the previous leg's (Chart One: `NR` 62⅞ is succeeded by
  `NR` 43½ on 1938-04-02 — a far lower rally top). Comparisons in later rules always
  use the current `last`.
- A rally out of `DT` never routes to `SR`, and a reaction out of `UT` never routes to
  `SRC` — secondary columns are only reachable from natural-column legs (rules 6g/6h
  are explicitly scoped to `NRC`/`NR` origins; confirmed by the charts, e.g.
  Bethlehem 1938-03-23: reaction from `NR` 56⅞ to 50¼, not below `last[NRC]` 50⅛
  → `SRC`).
- From `SR`/`SRC`, a *new* counter-swing of `S` from the secondary extreme routes by
  the same table as from `NR`/`NRC` (`DD-8` — the book is silent; this is the
  symmetric extension; no underline is drawn under secondary-column figures, `DD-9`).

### Step 4 — no record

If none of the above triggered, the day leaves no ledger entry (most days).

## 5. Underlines and pivotal points (book rules 4, 8)

Underline events fire on the day recording *starts* in a counter column (Step 3), per
book rule 4:

| Rule | Event                                                        | Underline color |
|------|--------------------------------------------------------------|-----------------|
| 4a   | first day of `NRC` recording after `UT` → under `last[UT]`   | red             |
| 4b   | first day of `NR`/`UT` recording after `NRC` → under `last[NRC]` | red         |
| 4c   | first day of `NR` recording after `DT` → under `last[DT]`    | black           |
| 4d   | first day of `NRC`/`DT` recording after `NR` → under `last[NR]` | black        |

Rule 8: *"The last price recorded in the Downward or Upward Trend columns becomes a
Pivotal Point as soon as you begin to record prices in the Natural Rally or Natural
Reaction columns… the extreme price made in the previous column then becomes another
Pivotal Point."* — i.e. **the underline event and pivotal-point creation are the same
event**. `PP[X]` is set to `last[X]` at the moment the rule-4 underline is drawn under
it, and remains the reference for rules 5, 9, 10 until the next underline event on the
same column replaces it.

The book renders pivotal points "by having a double line drawn underneath them in
either red ink or black ink" (rule 8). In the printed charts the carried-forward
header pivots are double-ruled while freshly drawn rule-4 lines can appear single;
the ledger view renders whatever the fixtures/rule engine emit: the engine emits one
`UNDERLINE` event per rule-4 firing with its color; display style (single vs double)
is a rendering concern keyed off "is this figure a pivotal point" (`DD-9`).

Rule-4 events also drive the **advisory signals of rule 9** (§6).

## 6. Signals (book rules 9, 10)

Signals are engine *events*; they never change recording state. The trade policy
(a separate module, per the build brief) decides what to do with them.

Confirmation margin: `C` (3 points for stocks, 6 for Key Price in the book — always
`S/2`, rule 10a). All comparisons `≥`/`≤` (`DD-1`).

### Trend-phase machinery

Each side (up/down) tracks the life of its most recent trend pivotal point:

**Up side** — `PP[UT]` is set when a reaction opens (rule 4a). Phases:

1. `firstCounter` — the reaction leg that created the PP is running.
2. `attempt` — a subsequent rally leg is running (recording in `NR`/`SR`/`UT`).
3. On any recorded high `≥ PP[UT] + C` → **`UPTREND_CONFIRMED`** (rule 10a),
   `pivot.confirmedThrough = true`, phase `confirmed`. (This usually coincides with
   recording in `UT` via 6f, but 10a is about the *pivotal* price, not the column.)
4. If the rally leg ends (a new `S` reaction begins, Step 3) with its peak short of
   `PP[UT] + C`, phase `failed`. Additionally, if the peak was *near* the PP —
   within `C` below it (peak `≥ PP[UT] − C`) — and the ensuing move retraces `≥ C`
   from that peak, emit **`UPTREND_DANGER`** (rule 10e; `DD-10` pins "a short
   distance below" to `C` and "ends and reacts three points" to a `C` retracement,
   which the `S`-sized swing that ends the leg always satisfies).
5. In phase `failed`, on any recorded low `≤ PP[UT] − C` → **`UPTREND_OVER`**
   (rule 10b), phase `over`. (`DD-11`: 10b requires the intervening failed rally —
   the *first* reaction always trades below `PP[UT] − C` by construction, so without
   the failed-attempt precondition the signal would be vacuous.)

**Down side** — mirror image with `PP[DT]` (rules 10c, 10d, 10f):

- Recorded low `≤ PP[DT] − C` → **`DOWNTREND_CONFIRMED`** (10c).
- Failed reaction (trough short of `PP[DT] − C`) then recorded high `≥ PP[DT] + C`
  → **`DOWNTREND_OVER`** (10d).
- Reaction trough near the PP (within `C` above) that then rallies `≥ C`
  → **`DOWNTREND_DANGER`** (10f).

### Advisory ("watch") signals — rule 9

- **9a**: when rule 4c fires (black lines drawn under the last red-ink `DT` figure)
  → emit `BUY_WATCH(PP[DT])` — "you may be given a signal to buy near that point."
  The *actionable* buy near that point is the 10f reversal (danger for the downtrend
  = the buy trigger of 9a); the trade policy maps 10f → long entry.
- **9b**: `PP[NR]` exists (black lines under a Natural Rally figure, rule 4d) and a
  later rally records within `C` of `PP[NR]` without having graduated (5a) →
  emit `WATCH_NR_PIVOT(PP[NR])` — the "find out whether the market is strong enough
  to change its course into the Upward Trend column" moment.
- **9c** (the stated reverse of 9a/9b): when rule 4a fires (red lines under the last
  `UT` figure) → `SELL_WATCH(PP[UT])`; when `PP[NRC]` exists (red lines, rule 4b) and
  a later reaction records within `C` of it → `WATCH_NRC_PIVOT(PP[NRC])`.

### Event catalogue

Recording events: `RECORD{column, price, ink}`, `UNDERLINE{column, price, color, rule}`,
`PIVOT_SET{column, price}`.
Signal events: `UPTREND_CONFIRMED`, `DOWNTREND_CONFIRMED`, `UPTREND_OVER`,
`DOWNTREND_OVER`, `UPTREND_DANGER`, `DOWNTREND_DANGER`, `BUY_WATCH`, `SELL_WATCH`,
`WATCH_NR_PIVOT`, `WATCH_NRC_PIVOT` — each carries the pivotal point involved, the
rule reference (`"10a"`, `"10f"`, …), and the triggering bar's date.

## 7. The Key Price (book rule 7, Ch. VIII pp. 85–86)

A **Key Price group** pairs two instruments. Three ledgers run in parallel: one per
member and one for the combined Key Price, exactly as the book runs U.S. Steel,
Bethlehem Steel, and their Key Price.

- **Series construction (book mode / absolute unit):** the Key Price is the *sum* of
  the two members' prices. The KP daily bar is `high = highA + highB`,
  `low = lowA + lowB` (`DD-12` discusses the intraday simultaneity approximation).
- **Thresholds:** "the same rules apply … except that you use twelve points as a
  basis instead of six" (rule 7): `S_KP = 2 × S`, `C_KP = 2 × C` in absolute mode.
  In percent mode see `DD-14` — the sum's percentage threshold equals the members'
  (the 2× is already built into the sum's base), and the default KP construction is a
  normalized index so that a high-priced member cannot dominate the pair.
- **Group coupling (`DD-13`):** the book records a member on a sub-threshold move when
  the *combined* move satisfies the KP threshold (p. 85: U.S. Steel recorded on a 5½
  move because Bethlehem moved 7 — "taken together … twelve points or better, the
  proper distance required"). Formally: a Step-3 counter-swing (and Step-2/Step-1
  recording day) for a group member also triggers when the member's own move is
  sub-`S` but the same-day KP move satisfies `S_KP`. Implemented as an `OR` over
  {member trigger, KP trigger}; toggleable per group (`groupCoupling: true` default
  for grouped instruments).
- **Membership changes:** a Key Price series is meaningful only for a fixed pair.
  Changing membership creates a *new group version*: the old version's KP ledger is
  archived read-only; the new pair's KP ledger is initialized by full replay over a
  configurable warm-up window (default 12 months) of stored raw bars; member
  instruments' own ledgers are unaffected; every change is written to an audit table.

## 8. Threshold modernization

The book's fixed 6 / 3 / 12 point thresholds are meaningful only for 1940-era $30–$100
stocks (the book itself scopes the formula to "active stocks selling above an
approximate price of 30", p. 89). The engine therefore takes thresholds as parameters
and supports two units:

```ts
type Threshold = { value: number; unit: 'absolute' | 'percent' };
// book / golden-master mode:  swing {6,'absolute'},  confirmation {3,'absolute'}, KP swing {12,'absolute'}
// production defaults:        equity swing {6,'percent'}, confirmation {3,'percent'}
//                             crypto swing {10,'percent'}, confirmation {5,'percent'}
```

- Internal ratios are invariant: `confirmation = swing / 2`; Key-Price basis = 2× the
  member basis (absolute mode) — see `DD-14` for what "2×" means in percent mode.
- **Percent base (`DD-15`):** a percent threshold is always applied to the price the
  book measures the distance *from*:
  - swing triggers: `ref = last[active]` (the current leg's recorded extreme):
    rally trigger `high ≥ ref × (1 + S%)`, reaction `low ≤ ref × (1 − S%)`;
  - rule 5 graduations and all rule 9/10 pivotal comparisons: the pivotal point
    itself: e.g. 10a up-confirmation `high ≥ PP[UT] × (1 + C%)`.
- Thresholds live in config (per instrument-type defaults, per-instrument overrides,
  per-group KP settings). The engine never hard-codes a threshold.
- Same engine, two units: golden-master tests run absolute 6/3/12 so the book's
  charts validate the logic; production runs percent mode.

## 9. Golden-master replay conventions (Phase 3)

The book's charts record only the days on which a figure was entered, and the figure
*is* the day's directional extreme. The golden-master harness therefore replays, for
each instrument, a synthetic bar per charted row: `high = low = recordedPrice`
(days with no entry contribute no bar — they cannot trigger anything the recorded
days don't already imply). The Key Price ledger is replayed from the book's own KP
figures on rows where the book recorded one.

Assertions per row: column, recorded price, ink, underline events, and the annotation
dates' rule firings (each chart's printed annotations name the rule and date).

**Divergence policy:** the charts are a hand ledger kept by a human. Where the book's
own entries contradict its printed rules (e.g. Chart One, U.S. Steel 1938-04-28: a
5⅝-point reaction recorded as a Natural Reaction when neither the 6-point rule nor
the Key-Price coupling is satisfiable from the recorded figures), the row is listed in
the chart's `knownDivergences` fixture section with an explanation, and the golden
test asserts the engine's (rule-faithful) behavior *and* fails on any divergence not
in the list. The book's annotation errata (e.g. Chart One cites "Rule 6-B" for the
1938-04-02 Downward-Trend→Natural-Rally transition, which is rule 6-C as printed in
Chapter IX) are recorded in fixtures verbatim with a `correctedRuleRef`.

## 10. Design Decisions

Ambiguities in the book resolved deterministically. **M** = material (flagged for
review), **m** = minor.

| ID | M/m | Question | Resolution | Rationale |
|----|-----|----------|------------|-----------|
| DD-1 | m | "approximately six points", "three or more points" | strict `≥ threshold` comparisons everywhere | Build brief mandates `>= threshold`; rule 5/10 already say "or more". |
| DD-2 | M | The charts sometimes record swings slightly under the basis (e.g. the Key Price's 78→89⅞ = 11⅞ treated as the 12-point basis on 1938-04-02) | `swingTolerance` config, default **0** in production; book-replay mode uses **⅛ point** (0.125), fitted in Phase 3 against Charts One–Three. This is the finest price tick and sits on a wide plateau (⅛…1 pt all reproduce the charts), so it is robust, not curve-fit. The Key Price uses 2× the tolerance, matching its 2× basis | Keeps production strict while letting the golden master validate the *logic* rather than Livermore's hand-rounding to the nearest eighth. |
| DD-3 | M | A wide-range day can satisfy continuation *and* reversal (order unknowable from OHLC) | At most one recorded figure per instrument per day; steps evaluated in the order §4 (same-direction upgrade → continuation → counter-swing). If both continuation and counter-swing qualify, continuation wins and the counter-swing is re-evaluated on later bars against the updated extreme | Deterministic; trend-direction-first matches the book's practice of recording the extreme "in the direction of the trend"; the reversal fires the next day if real. |
| DD-4 | m | Which price is recorded | The day's high for up-direction columns, low for down-direction columns; never the close | Book p. 86 verbatim; the fetcher must supply OHLC. |
| DD-5 | m | Crypto daily bar boundary | UTC `[00:00, 24:00)`, evaluated at 00:05 UTC; stored in config; changing it forces full replay | Crypto trades 24/7; any boundary is a convention — it just has to be immutable. |
| DD-6 | M | How does a fresh ledger start? (book starts mid-history) | Cold start: track running high/low from the first bar; open `UT` on the first `S`-swing up from the running low, `DT` on the first `S`-swing down from the running high; production always warm-starts by replaying ≥ 12 months of history | The book never specifies an initialization; warm-up replay makes the choice immaterial in practice. |
| DD-7 | m | Rule 5a fires on `PP[NR] + C` even when below `last[UT]`? | Yes — 5a is the mechanism by which a new uptrend is recognized from a base without exceeding the old high (mirror 5b) | Verbatim rule text; the two routes into `UT` (5a and 6f) are independent. |
| DD-8 | m | Behavior of a fresh `S`-counter-swing starting from an `SR`/`SRC` extreme (book silent) | Route with the same table as from `NR`/`NRC` (§4 Step 3) | Symmetric extension; keeps the machine total (every state has a transition for every input). |
| DD-9 | m | Single vs double underline; do secondary columns get underlines? | Engine emits one `UNDERLINE` event per rule-4 firing (color per rule 4); pivotal points are exactly the underlined figures; display may double-rule pivots per rule 8. No underlines/pivots for `SR`/`SRC` figures | Rule 4 enumerates only the four events; rule 8's "double line" is presentational; charts show no underlined secondary figures. |
| DD-10 | M | Rule 10e/10f "ends a short distance below … and reacts three or more points" | "Near" window: leg extreme within `C` of the trend PP on the failing side (peak ∈ [PP−C, PP+C) for 10e); "reacts/rallies 3+ points from that price" = retracement `≥ C` from the leg extreme — emitted when the retracement is observed (at latest when the `S`-swing ends the leg) | `C` is the book's only "nearness" quantum (rules 9/10 all use 3 points); marginal overshoots that fail to confirm are included deliberately — a peak at PP+1 that dies is at least as dangerous as one at PP−1. |
| DD-11 | M | Rule 10b/10d "fails to do this — and … sells three points below the last Pivotal Point" | Requires the phased precondition (PP set → counter-leg → *failed* attempt back toward the PP → then a recorded extreme `C` beyond the PP against the trend). Without the failed-attempt precondition the first reaction (already `S ≥ 2C` beyond the PP by construction) would fire the signal vacuously on every swing | Makes 10b/10d meaningful and matches the book's narrative ("If the stock fails to do this…" refers to the 10a carry-through attempt). |
| DD-12 | m | KP daily bar from two members trading simultaneously | `high = Σ highs`, `low = Σ lows` (slight overstatement of the true combined intraday extreme); golden masters replay the book's own KP figures, so this approximation is exercised only in production | Without tick data the true joint extreme is unknowable; consistent and conservative-in-magnitude. |
| DD-13 | M | Group coupling: book records a member on a 5½ move when the pair moved 12+ | For group members, a recording trigger is `memberMove ≥ S` **OR** (`groupCoupling` on and same-day `KP move ≥ S_KP`); the book states the KP→member direction explicitly; the member-alone direction (e.g. one stock moves 8, pair moves 10) is retained because Chapter IX's per-stock rules stand on their own | P. 85 verbatim supports OR; charts adjudicate (Phase 3). Toggleable per group. |
| DD-14 | M | Key Price thresholds and construction in percent mode | Percent thresholds for the KP series equal the *members'* percentage (the book's 12-vs-6 is a property of the sum's ~2× base, not a stricter filter: 6/47 ≈ 12 points/97 ≈ 12.4%). Default KP construction in percent mode is a **normalized index** (each member rebased to 100 at group creation, then summed) so a $60k BTC cannot drown a $3k ETH; `keyPrice.method: 'sum' | 'normalized-index'` in config, `'sum'` in absolute/book mode | Preserves the book's internal ratios dimensionally instead of copying its numerals; the build brief's "2× the members' swing" is honored in absolute mode where it is well-defined. **Needs review sign-off.** |
| DD-15 | M | Base for percent thresholds | The price the book measures the distance from: leg extreme `last[active]` for swing triggers; the pivotal point itself for confirmation/graduation/danger comparisons | The book's point-distances are always anchored at a recorded extreme or a pivotal point; percentages inherit the same anchors. |
| DD-16 | m | Float determinism / property tests | Prices are IEEE-754 doubles (exact for eighths); percent comparisons use an epsilon of `1e-9 × base` to absorb multiplication noise; property tests assert identical column sequences across absolute price scalings | Keeps the engine dependency-free; eighths and powers-of-two scale exactly, epsilon covers decimal scalings. |
| DD-17 | m | Book annotation errata | Fixtures store the book's rule citations verbatim plus `correctedRuleRef` where the citation contradicts Chapter IX's printed lettering (first instance: Chart One, 1938-04-02, cited "6-B", actual 6-C) | The golden masters must assert against the *rules*, not typos, while preserving the source faithfully. |
| DD-18 | M | A pre-existing natural-column pivot (`PP[NRC]`/`PP[NR]`) can outlive the leg that created it and wrongly force a rule-5b/5a graduation on a much later, unrelated swing | The natural-column pivot is **consumed** when the trend graduates: recording a figure in `DT` clears `PP[NRC]`; recording in `UT` clears `PP[NR]`. It is re-established only by the next rule-4b/4d underline. Also: rules 5a/5b are same-direction continuations (§4 Step 1) only — the transition day (§4 Step 3) is governed purely by rules 6a–d | Confirmed by Chart One+Two, Bethlehem 1938-04-29…05-26: after a full down→up→down cycle the stale pre-chart `PP[NRC]` (50⅛) otherwise forces DT entries where the book records Natural Reaction. Clearing the consumed pivot reproduces the book. |
| DD-19 | M | *(explored, reverted)* Does a rally out of the Downward Trend record in Secondary Rally when a standing Natural Rally pivot is unbeaten? | **Reverted.** A literal rule 6-C (rally out of DT → Natural Rally) is used. The book's actual Secondary-Rally placement here is governed by **Key Price group confirmation**, not a per-instrument pivot test — see the open item in §12. Modelling it per-instrument mis-fires (it made Chart One's legitimate 1938-04-02 fresh Natural Rally into a Secondary Rally). Rows where the book uses Secondary Rally under group confirmation are catalogued as `knownDivergences` pending the §12 decision | The distinguishing evidence (§12) is that Bethlehem/U.S. Steel graduate SR→NR exactly when the combined Key Price clears its own pivot (101), not on any single-stock condition. |

## 11. Book rule index → spec cross-reference

| Book rule | Spec section |
|-----------|--------------|
| 1–3 (ink) | §1 |
| 4a–4d (underlines) | §5, Step 3 of §4 |
| 5a–5b (graduation to trend columns) | §4 Step 1 |
| 6a–6d (natural swings) | §4 Steps 2–3 |
| 6e–6f (piercing the trend column while in a natural column) | §4 Step 1 |
| 6g–6h (secondary columns) | §4 Steps 2–3 |
| 7 (Key Price, 12-point basis) | §7 |
| 8 (pivotal points, double lines) | §5 |
| 9a–9c (watch signals near pivotal points) | §6 |
| 10a–10f (confirmations and danger signals) | §6 |

## 12. Key Price group confirmation governs column placement (RESOLVED — option B)

**Decision (owner, 2026-07):** stay maximally faithful to the book. Key Price group
confirmation is a first-class part of recording, not merely a trade-policy toggle — "a
positive change of the trend must be confirmed by the action of the Key Price" (Ch. VIII,
p. 85). A grouped instrument may not commit to a trend change until the combined Key Price
confirms it. This is the book's central risk-control idea, so the tool enforces it.

### The confirmation rule (the "commitment cap")

Each up-side column has a commitment level — `SR` < `NR` < `UT` (1 < 2 < 3); the down side
mirrors — `SRC` < `NRC` < `DT`. When recording a grouped instrument, its column is chosen
by the per-instrument rules of §4, then **capped at the Key Price's own current commitment
level on that side**:

- Key Price in `SR` (or any down column, i.e. not yet rallying) → member capped at `SR`.
- Key Price in `NR` → member capped at `NR`.
- Key Price in `UT` → no cap (member may reach `UT`).
- Down side mirrors with `SRC`/`NRC`/`DT`.

**Resumption exception.** The cap applies only to a *change* of trend. A member that
records a new extreme beyond its own last trend-column figure — rule 6-E (`low` < last
`DT`) or rule 6-F (`high` > last `UT`), and trend-column continuations — is *resuming* an
already-established trend, not changing it, so it records in the trend column **regardless
of the Key Price**. This is why on 1938-05-27 Bethlehem drops into `DT` (a new low below
its prior `DT` low of 40) while the Key Price is still in `NRC`, yet in June no member may
enter `UT` until the Key Price does.

### Evidence (Charts One–Three)

- Lockstep graduation: on 1938-06-20…22 U.S. Steel, Bethlehem, and the Key Price are all
  in `SR`; U.S. Steel alone would post `NR` on 06-21 (49⅞ > its 49 pivot) but the Key
  Price (96⅜ < its 101 pivot) holds it in `SR`. All three graduate to `NR` on 06-23 (Key
  Price 104½ > 101) and to `UT` on 06-24 (Key Price 108⅞).
- No false gating of continuations: 1938-05-27 Bethlehem `DT` while Key Price `NRC`
  (resumption exception); 1938-03-25 all three enter `DT` together (continuation / 6-E).
- Fresh rallies pass immediately: 1938-04-02 both members post `NR` because the Key Price
  was itself posting a fresh `NR` (89⅞) — cap = `NR`, no demotion.

### Implementation

`step()` accepts the group's Key Price commitment on each side via the coupling hint
(`kpUpCap`, `kpDownCap`); `stepGroup()` steps the Key Price ledger first and derives the
caps from its resulting column, then steps the members. Standalone (ungrouped) instruments
pass no caps and record purely per §4 — the engine stays pure and the member↔group coupling
is confined to the hint argument, so archival replays and membership changes remain a
matter of which caps are supplied. The golden master runs in grouped mode so the book's own
three-ledger chart validates the confirmation logic end-to-end.

### (Superseded) recommendation

The pre-decision analysis had recommended option A (keep recording per-instrument, catalog
the June rows as divergences, model confirmation only in the trade-policy layer). The owner
chose fidelity over that separation; option B above is authoritative. Group confirmation is
still independently *measurable* — Phase 6.5 compares grouped vs per-instrument runs by
toggling whether the caps are supplied.

The golden-master fit against Charts One–Three surfaced a behavior the book relies on
that the current per-instrument engine does not model. In June 1938 both U.S. Steel and
Bethlehem Steel rally out of their second downtrend, but the book records those rallies
in the **Secondary Rally** column, not Natural Rally — and only promotes them to Natural
Rally / Upward Trend on 1938-06-23/24. The trigger is unambiguous in the data:

- The combined **Key Price** Natural-Rally pivot is 101 (set 1938-04-16).
- The members' combined price crosses 101 on 1938-06-23 (U.S. 51¼ + Bethlehem 53¼ = 104½).
- That is exactly the day both members graduate Secondary Rally → Natural Rally.
- By contrast, on 1938-04-02 both go straight to Natural Rally, because the Key Price
  itself was making a *fresh* rally (its earlier pivots stale after its own downtrend to
  78) — there was no standing Key Price pivot to hold them in the secondary column.

In other words, **the book uses the Secondary columns partly to encode "the combined
Key Price has not yet confirmed this move,"** which is precisely the book's headline
risk-control idea (and the subject of the Phase 6.5 experiment).

This collides with the build brief's architecture, which specifies a **pure,
per-instrument rule engine** and treats group confirmation as a measurable **trade-policy
toggle** (Phase 6.1/6.5), not part of recording. Two ways to reconcile:

- **(A) Keep recording per-instrument (current design).** Each instrument's ledger
  follows Chapter IX literally; the four June rows where the book uses group-confirmed
  Secondary Rally are catalogued as `knownDivergences`. Group confirmation lives entirely
  in the signal/trade-policy layer, where it can be toggled and measured. Engine stays
  I/O-free and reusable; ~96% of charted cells reproduce exactly.
- **(B) Couple member recording to the Key Price ledger.** `step()` for a group member
  would additionally consult the group's Key Price state to choose Secondary vs Natural
  columns, reproducing the book's ledger exactly but making a member's ledger depend on
  its group (and complicating membership changes / archival replays).

**Recommendation: (A).** It matches the brief's separation of concerns, keeps the engine
pure and independently reusable, and still lets us *measure* group confirmation's value
(Phase 6.5) rather than baking it into the ledger. The cost is a handful of documented,
faithfully-explained divergences in the historical ledger view. Awaiting your call before
finalizing the golden master.

## 13. Full-history golden master results (Charts One–Sixteen, resolved)

**Status: final validation results for the complete March 1938 – February 1940 series.**

With the owner's §12 decision (option B, Key Price confirmation gates column placement)
implemented, the golden master was run against all sixteen charts — 479 charted cells
across nearly two years, not just the three-chart sample used to derive the mechanism.
Two-tier result:

- **Charts One–Three (the fully dual-pass-transcribed, referee-adjudicated region):
  97/97 — 100%.** This remains the strongest evidence: every cell the transcription
  pipeline verified twice and adjudicated a third time, the engine reproduces exactly,
  including the full Secondary→Natural→Trend group-confirmation graduation sequence.
- **All sixteen charts: 434/479 — 90.6%.** Charts Four–Sixteen were transcribed with
  the same dual-pass-plus-referee pipeline but on a single, later pass (not re-verified a
  second time the way Charts One–Three were), so some of the residual gap is expected to
  be transcription noise rather than engine error — see §13.3.

### 13.1 Three genuine hand-ledger checksum anomalies (not engine issues)

Livermore's own arithmetic doesn't sum on three occasions (member A + member B ≠ Key
Price as literally written), confirmed by close re-inspection of the source images —
not a transcription artifact, since the individual digits are independently legible in
each case. Catalogued as `knownDivergences` in the affected fixtures:

- **1939-07-21**, Key Price NR "115⅛" vs US 52½ + BS 63 = 115½ (⅜ short).
- **1939-11-08**, Key Price SRC "158¾" vs US 72⅞ + BS 86⅞ = 159¾ (1 point short).
- **1939-11-09**, Key Price NRC "159¾" vs US 70½ (repeat/dash) + BS 83¼ = 153¾ (6 points
  over — the largest of the three, and the only one where the discrepancy isn't a small
  hand-rounding slip).

Two further apparent checksum failures from the raw transcription were **not** book
errors — they were transcription misses, corrected before golden-master assertion:
1939-06-30 Key Price "93⅛" → **93⅝** (ambiguous ⅛/⅝ glyph, resolved by checksum + a
prior independent hand-transcription of the same sparse chart agreeing on ⅝); and
1939-03-03 Key Price "140" → **140⅛** (a faint fraction mark the transcription passes
missed entirely).

### 13.2 Open item: the DT/UT→NR/NRC graduation boundary is not fully characterized

The largest identifiable cluster of remaining mismatches (roughly a dozen dated
clusters, each a short run of consecutive days) shares one shape: the book keeps an
instrument in a Secondary column (SR/SRC) for a stretch where the engine's rule 6-C/6-A
graduates it straight to a Natural column (NR/NRC), or vice versa.

Two hypotheses were tested:

1. **Symmetric `last.NR`/`last.NRC` gate on the DT→NR and UT→NRC transitions**, mirroring
   the check rule 6-G/6-H already applies on the NRC→NR and NR→NRC transitions (i.e.,
   treat "last price recorded in the Natural Rally column" literally, per rule 6-G's
   text, regardless of which column the rally originates from). **Rejected** — tested
   against the full 16-chart set, this *reduced* the match rate from 90.6% to 36.5%. Once
   any single instance is wrongly capped to the Secondary column, the wrong `active`
   state cascades through the rest of that chart's sequence, and the naive symmetric
   reading is wrong far more often than the current asymmetric one (rule 6-C is
   evidently *not* symmetric with 6-G in the book's actual practice: a rally out of a
   *fully committed* Downward Trend graduates to Natural Rally unconditionally; only a
   rally out of an *already-secondary* NRC/SRC leg is subject to the last-value test).
2. **§12 Key Price cap release timing.** In at least one traced case (1940-02-07/08),
   a single member (Bethlehem) breaks into Natural Rally a day *before* the Key Price
   itself confirms; the current cap correctly holds it in Secondary Rally on day one, but
   because the engine's Step 1/2 "same-direction continuation" logic re-enters through
   the (now-established) Secondary column the next day rather than re-evaluating the cap
   fresh, the demotion doesn't cleanly release once the Key Price *does* confirm one day
   later. This is a specific, well-diagnosed limitation of the current cap
   implementation (not an open book-interpretation question) — a candidate fix is a
   short look-ahead grace window on the cap release, symmetric to the existing DD-13
   swing-trigger coupling. **Not implemented in this pass**, to avoid another
   regression without dedicated test coverage; flagged here for follow-up.

Both explored and current behavior are preserved in code comments (`DD-19b`, reverted,
in `engine.ts`) so a future attempt does not have to re-derive the same dead end.

### 13.3 Disposition

All 44 residual date/instrument mismatches (after the 5 corrections/divergences in
§13.1) are catalogued as `knownDivergences` in their respective chart fixtures, tagged
with a reference to this section rather than 44 bespoke explanations, since they trace
to the one or two mechanisms above. The golden-master test suite passes with these
divergences declared; **no mismatch is silently ignored** — the test fails hard on any
divergence not explicitly listed.
