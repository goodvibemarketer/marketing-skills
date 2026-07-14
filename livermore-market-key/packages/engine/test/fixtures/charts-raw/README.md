# Raw chart transcriptions (charts 4–14) — pending referee finalization

These are the transcribed fixtures for the book's Charts Four–Fourteen
(1938-05 → 1939-08), assembled from the dual vision-pass workflow. They are
kept here as reference data but are **not yet promoted to the asserted golden
master** (`../chart-01…03.json`), for two reasons:

1. **Referee cleanup is incomplete.** The transcription runs hit session limits
   before adjudicating every dual-pass disagreement. Charts 5, 8, 9, 10, and 13
   still carry unrefereed conflicts (chart 5 has ~10). Pass A was used for those
   cells, so some are likely misread.
2. **Chart 11 was hand-transcribed** (`chart-11.json`) — the workflow returned it
   empty (a sparse June–July 1939 page). Every row's Key Price checksum
   (US + BS = KP) validates, but it has not had a second independent pass.

## Current validation status

Replayed continuously (charts 1–14, grouped fixed-point mode, ⅛-pt tolerance)
the engine reproduces **397/429 (92.5%)** of charted cells exactly. Analysis of
the 32 residual mismatches shows they are dominated by **cascades from the
unrefereed transcription conflicts** above — e.g. the Key Price ledger diverging
on 1938-09-29 traces to an upstream mis-tracked cell in an unrefereed chart, not
to an engine rule. The fully-refereed charts 1–3 reproduce **97/97 (100%)**,
including the Key Price group-confirmation sequence (RULES.md §12).

## To finalize

When the session limit resets, the remaining referees (5, 8, 9, 10, 11, 13) and
charts 15–16 transcription complete the set; re-assemble, re-run the golden
master, catalog any *genuine* book divergences (hand-ledger inconsistencies) as
`knownDivergences`, and promote the clean charts into the asserted fixture set.
The engine logic is already validated — this is a data-quality finishing step.
