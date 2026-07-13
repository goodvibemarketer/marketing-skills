# Golden-master fixtures — Charts One–Sixteen (book pp. 102–133)

These fixtures transcribe the worked example in *How to Trade in Stocks*
(1940): U.S. Steel, Bethlehem Steel, and their combined Key Price, recorded
daily from late March 1938 to February 1940 across sixteen two-page chart
spreads, with the book's own dated annotations naming the rule that fired.

## Transcription methodology

Each spread was rendered at 400 dpi from a scan of the 1940 first edition and
transcribed by **two independent vision passes**; every cell-level disagreement
(price, column, ink, underline) was adjudicated by a **third referee pass**
against the page images. Two mechanical validators then ran over the result:

- **Key Price checksum** — the book's KP figure equals U.S. Steel + Bethlehem
  on every row where all three are recorded; violations were re-inspected.
- **Calendar checks** — rows advance strictly, Monday–Saturday only (the NYSE
  traded Saturdays in 1938–40); `SAT`-prefixed labels must fall on Saturdays;
  the label's day-of-month must match the inferred ISO date.

## Fixture schema (`chart-NN.json`)

```jsonc
{
  "chart": 1,
  "bookPages": [102, 103],
  "headerEntries": [ /* carried-forward pivotal points printed above the DATE row */ ],
  "rows": [
    { "date": "1938-03-23", "dateLabel": "MAR23", "cells": [
      { "instrument": "US",          // US | BS | KP
        "column": "DT",              // SR | NR | UT | DT | NRC | SRC
        "price": "47",               // integer + eighths fraction, e.g. "43 1/2"
        "ink": "red",                // black | red | blue (blue = the book's pencil)
        "underline": "none",         // none | single | double (hand-drawn lines)
        "underlineColor": "none" }   // black | red | mixed | none
    ]}
  ],
  "annotations": [
    { "text": "…verbatim printed note…",
      "ruleRefs": ["6-B", "4-C"],          // as printed in the book
      "correctedRuleRefs": ["6-C", "4-C"], // where the book's citation contradicts Ch. IX (DD-17)
      "dateRefs": ["1938-04-02"] }
  ],
  "knownDivergences": [
    // Rows where the book's hand ledger contradicts its own printed rules.
    // The golden test tolerates ONLY what is listed here, each with a reason.
    { "date": "1938-04-28", "instrument": "US", "kind": "book-extra-entry",
      "reason": "5 5/8-point reaction recorded as Natural Reaction; see RULES.md DD-2" }
  ]
}
```

`underline` marks hand-drawn lines hugging a figure (the pivotal-point
marking of rules 4/8), not the printed grid. The underline is stored on the
cell it is drawn under; the engine event that draws it fires on the first day
of counter-column recording, which is typically a few rows later.
