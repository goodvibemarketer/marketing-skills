# Livermore Market Key — Tracking Tool

A modern implementation of the price-recording method from Jesse L. Livermore,
*How to Trade in Stocks* (1940): the six-column ledger, pivotal points,
underline conventions, and buy/danger signals — driven by a pure, deterministic
rule engine with automated daily price ingestion for stocks and crypto.

**Status: Phase 1–3 (spec, engine, golden-master fixtures). Application layers
(Phases 4–6) are gated on review of these artifacts.**

## Layout

| Path | Contents |
|------|----------|
| `RULES.md` | The formal spec: state machine, transition rules, pivotal points, signals, threshold modernization, and every ambiguity resolution (Design Decisions DD-1…DD-17) |
| `packages/engine` | Pure rule engine (`(state, dailyBar, config) → (state', events[])`) — zero I/O dependencies |
| `packages/engine/test/fixtures` | Golden-master fixtures transcribed from the book's Charts One–Sixteen (pp. 102–133) |
| `packages/engine/test` | Per-rule unit tests, percent-mode property tests, golden-master replay |

## Calibration note (fixed points vs percentages)

The book's thresholds are **fixed dollar points** calibrated for 1940-era
$30–$100 stocks: a 6-point swing moves recording between columns, a 3-point
carry-through past a pivotal point confirms, and the two-stock Key Price uses
12/6. Fixed dollar thresholds are meaningless across a $40 stock, a $500 stock,
and a $60,000 crypto asset, so production runs **percentage thresholds**
(defaults: equities 6%/3%, crypto 10%/5%, per-instrument overrides in config).

Because the original charts use fixed points, the golden-master suite runs the
engine in **fixed-point mode** — thresholds expressed as absolute values
(6 / 3 / 12) — so the book's own charts validate the logic. Production runs the
*same engine* in percent mode. Thresholds are typed as
`{ value: number, unit: 'absolute' | 'percent' }` and always live in config,
never in the engine.

Internal ratios from the book are invariants: confirmation = swing / 2; the
Key Price basis is 2× the single-instrument basis (see RULES.md DD-14 for what
"2×" means in percent mode — the sum's base is already ~2×, so the KP percent
equals the members' percent, and the default KP construction for mixed-price
pairs is a normalized index).

## Testing

```sh
npm install
npm test            # runs all workspaces
```

The engine test suite has three layers (Phase 3):

1. **Golden masters** — the transcribed charts replayed in fixed-point mode;
   the suite fails on any divergence from the book not explicitly listed (with
   a reason) in a fixture's `knownDivergences`.
2. **Per-rule unit tests** — each of rules 4a–d, 5a–b, 6a–h, 7, 8, 9a–c, 10a–f
   in isolation.
3. **Property tests** — percent mode is scale-invariant: the same relative
   price path produces identical ledgers at any absolute price level.
