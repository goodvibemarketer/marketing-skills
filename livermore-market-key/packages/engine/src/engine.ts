/**
 * The Livermore Market Key recording state machine (RULES.md §4–§6).
 *
 * Pure function: (state, bar, config, coupling?) → (state', events[]).
 * No I/O, no clock, no randomness. Bars must be fed in strict
 * chronological order, gap-free per the data layer's contract.
 */

import {
  type Bar,
  type Column,
  type CouplingHints,
  type EngineConfig,
  type EngineEvent,
  type LedgerState,
  type StepResult,
  initialState,
  inkFor,
  isUp,
} from './types.js';
import {
  confDownTarget,
  confUpTarget,
  gt,
  gte,
  lt,
  lte,
  swingDownTarget,
  swingUpTarget,
} from './thresholds.js';

function clone(s: LedgerState): LedgerState {
  return {
    ...s,
    last: { ...s.last },
    pivot: {
      UT: s.pivot.UT ? { ...s.pivot.UT } : null,
      DT: s.pivot.DT ? { ...s.pivot.DT } : null,
      NR: s.pivot.NR ? { ...s.pivot.NR } : null,
      NRC: s.pivot.NRC ? { ...s.pivot.NRC } : null,
    },
    anchor: s.anchor ? { ...s.anchor } : null,
  };
}

export function step(
  state: LedgerState,
  bar: Bar,
  cfg: EngineConfig,
  coupling?: CouplingHints,
): StepResult {
  const s = clone(state);
  const events: EngineEvent[] = [];
  const date = bar.date;

  const record = (column: Column, price: number, rule: string): void => {
    s.last[column] = price;
    s.active = column;
    events.push({ type: 'RECORD', date, column, price, ink: inkFor(column), rule });
  };

  const underline = (column: 'UT' | 'DT' | 'NR' | 'NRC', color: 'red' | 'black', rule: string): void => {
    const price = s.last[column];
    if (price === null) return;
    events.push({ type: 'UNDERLINE', date, column, price, color, rule });
    events.push({ type: 'PIVOT_SET', date, column, price });
    s.pivot[column] = { price, color, setOn: date, confirmedThrough: false };
  };

  const signal = (
    kind: import('./types.js').SignalKind,
    rule: string,
    pivotColumn: 'UT' | 'DT' | 'NR' | 'NRC',
  ): void => {
    const pp = s.pivot[pivotColumn];
    if (!pp) return;
    events.push({ type: 'SIGNAL', date, kind, rule, pivot: { column: pivotColumn, price: pp.price } });
  };

  /* ---------------------------------------------------------------- */
  /* Anchoring (DD-6): before the first S-swing there is no column.    */
  /* ---------------------------------------------------------------- */
  if (s.active === null) {
    if (s.anchor === null) {
      s.anchor = { hi: bar.high, hiDate: date, lo: bar.low, loDate: date };
      return { state: s, events };
    }
    const upDist = bar.high - s.anchor.lo;
    const downDist = s.anchor.hi - bar.low;
    const upTrig = gte(bar.high, swingUpTarget(s.anchor.lo, cfg));
    const downTrig = lte(bar.low, swingDownTarget(s.anchor.hi, cfg));
    if (upTrig || downTrig) {
      // A single bar could satisfy both; take the larger excursion (deterministic).
      if (upTrig && (!downTrig || upDist >= downDist)) {
        record('UT', bar.high, 'anchor-up (DD-6)');
      } else {
        record('DT', bar.low, 'anchor-down (DD-6)');
      }
      s.anchor = null;
      return { state: s, events };
    }
    s.anchor.hi = Math.max(s.anchor.hi, bar.high);
    s.anchor.lo = Math.min(s.anchor.lo, bar.low);
    if (bar.high === s.anchor.hi) s.anchor.hiDate = date;
    if (bar.low === s.anchor.lo) s.anchor.loDate = date;
    return { state: s, events };
  }

  const active: Column = s.active;
  const legWasUp = isUp(active);

  /* ---------------------------------------------------------------- */
  /* Steps 1–2: same-direction upgrade & continuation (§4)             */
  /* ---------------------------------------------------------------- */
  let recordedSameDir = false;

  if (legWasUp) {
    const lastActive = s.last[active];
    if (s.last.UT !== null && gt(bar.high, s.last.UT)) {
      record('UT', bar.high, active === 'UT' ? '6-continuation' : '6f');
      recordedSameDir = true;
    } else if (
      active !== 'UT' &&
      s.pivot.NR !== null &&
      gte(bar.high, confUpTarget(s.pivot.NR.price, cfg))
    ) {
      record('UT', bar.high, '5a');
      s.watchNRPending = false;
      recordedSameDir = true;
    } else if (active === 'SR' && s.last.NR !== null && gt(bar.high, s.last.NR)) {
      record('NR', bar.high, '6g-resume');
      recordedSameDir = true;
    } else if (lastActive !== null && gt(bar.high, lastActive)) {
      record(active, bar.high, '6-continuation');
      recordedSameDir = true;
    }
  } else {
    const lastActive = s.last[active];
    if (s.last.DT !== null && lt(bar.low, s.last.DT)) {
      record('DT', bar.low, active === 'DT' ? '6-continuation' : '6e');
      recordedSameDir = true;
    } else if (
      active !== 'DT' &&
      s.pivot.NRC !== null &&
      lte(bar.low, confDownTarget(s.pivot.NRC.price, cfg))
    ) {
      record('DT', bar.low, '5b');
      s.watchNRCPending = false;
      recordedSameDir = true;
    } else if (active === 'SRC' && s.last.NRC !== null && lt(bar.low, s.last.NRC)) {
      record('NRC', bar.low, '6h-resume');
      recordedSameDir = true;
    } else if (lastActive !== null && lt(bar.low, lastActive)) {
      record(active, bar.low, '6-continuation');
      recordedSameDir = true;
    }
  }

  /* ---------------------------------------------------------------- */
  /* Step 3: counter-swing transition (§4). Skipped when a             */
  /* same-direction figure was recorded today (DD-3).                  */
  /* ---------------------------------------------------------------- */
  if (!recordedSameDir) {
    const ref = s.last[active];
    if (ref !== null) {
      if (legWasUp) {
        const ownTrigger = lte(bar.low, swingDownTarget(ref, cfg));
        const coupled = (coupling?.kpRecordedDown ?? false) && lt(bar.low, ref);
        if (ownTrigger || coupled) {
          const couplingTag = ownTrigger ? '' : ' (KP coupling, DD-13)';
          // Underlines / pivotal points for the column being left (rules 4a, 4d).
          if (active === 'UT') {
            underline('UT', 'red', '4a');
            s.upPhase = 'firstCounter';
            signal('SELL_WATCH', '9c', 'UT');
          } else if (active === 'NR') {
            underline('NR', 'black', '4d');
            s.watchNRPending = true;
          }
          // 10e final check: the rally attempt ended without confirmation.
          if (s.upPhase === 'attempt' && s.pivot.UT) {
            const peak = Math.max(s.attemptExtreme ?? bar.high, bar.high);
            if (
              !s.dangerEmitted &&
              lt(peak, confUpTarget(s.pivot.UT.price, cfg)) &&
              gte(peak, confDownTarget(s.pivot.UT.price, cfg))
            ) {
              signal('UPTREND_DANGER', '10e', 'UT');
              s.dangerEmitted = true;
            }
            s.upPhase = 'failed';
          }
          // Routing (§4 Step 3 table).
          if (active === 'UT') {
            if (s.last.DT !== null && lt(bar.low, s.last.DT)) {
              record('DT', bar.low, `6e${couplingTag}`);
            } else if (s.pivot.NRC !== null && lte(bar.low, confDownTarget(s.pivot.NRC.price, cfg))) {
              record('DT', bar.low, `5b${couplingTag}`);
            } else {
              record('NRC', bar.low, `6a${couplingTag}`);
            }
          } else {
            const fromRule = active === 'NR' ? '6b' : '6b (DD-8)';
            if (s.last.DT !== null && lt(bar.low, s.last.DT)) {
              record('DT', bar.low, `${fromRule}-tail${couplingTag}`);
            } else if (s.pivot.NRC !== null && lte(bar.low, confDownTarget(s.pivot.NRC.price, cfg))) {
              record('DT', bar.low, `5b${couplingTag}`);
            } else if (s.last.NRC === null || lt(bar.low, s.last.NRC)) {
              record('NRC', bar.low, `${fromRule}${couplingTag}`);
            } else {
              record('SRC', bar.low, `6h${couplingTag}`);
            }
          }
          // Down side: a new reaction leg begins — an attempt toward PP[DT]?
          if (s.pivot.DT && (s.downPhase === 'firstCounter' || s.downPhase === 'failed')) {
            s.downPhase = 'attempt';
          }
          s.attemptExtreme = bar.low;
          s.dangerEmitted = false;
        }
      } else {
        const ownTrigger = gte(bar.high, swingUpTarget(ref, cfg));
        const coupled = (coupling?.kpRecordedUp ?? false) && gt(bar.high, ref);
        if (ownTrigger || coupled) {
          const couplingTag = ownTrigger ? '' : ' (KP coupling, DD-13)';
          if (active === 'DT') {
            underline('DT', 'black', '4c');
            s.downPhase = 'firstCounter';
            signal('BUY_WATCH', '9a', 'DT');
          } else if (active === 'NRC') {
            underline('NRC', 'red', '4b');
            s.watchNRCPending = true;
          }
          if (s.downPhase === 'attempt' && s.pivot.DT) {
            const trough = Math.min(s.attemptExtreme ?? bar.low, bar.low);
            if (
              !s.dangerEmitted &&
              gt(trough, confDownTarget(s.pivot.DT.price, cfg)) &&
              lte(trough, confUpTarget(s.pivot.DT.price, cfg))
            ) {
              signal('DOWNTREND_DANGER', '10f', 'DT');
              s.dangerEmitted = true;
            }
            s.downPhase = 'failed';
          }
          if (active === 'DT') {
            if (s.last.UT !== null && gt(bar.high, s.last.UT)) {
              record('UT', bar.high, `6f${couplingTag}`);
            } else if (s.pivot.NR !== null && gte(bar.high, confUpTarget(s.pivot.NR.price, cfg))) {
              record('UT', bar.high, `5a${couplingTag}`);
            } else {
              record('NR', bar.high, `6c${couplingTag}`);
            }
          } else {
            const fromRule = active === 'NRC' ? '6d' : '6d (DD-8)';
            if (s.last.UT !== null && gt(bar.high, s.last.UT)) {
              record('UT', bar.high, `${fromRule}-tail${couplingTag}`);
            } else if (s.pivot.NR !== null && gte(bar.high, confUpTarget(s.pivot.NR.price, cfg))) {
              record('UT', bar.high, `5a${couplingTag}`);
            } else if (s.last.NR === null || gt(bar.high, s.last.NR)) {
              record('NR', bar.high, `${fromRule}${couplingTag}`);
            } else {
              record('SR', bar.high, `6g${couplingTag}`);
            }
          }
          if (s.pivot.UT && (s.upPhase === 'firstCounter' || s.upPhase === 'failed')) {
            s.upPhase = 'attempt';
          }
          s.attemptExtreme = bar.high;
          s.dangerEmitted = false;
        }
      }
    }
  }

  /* ---------------------------------------------------------------- */
  /* Signal evaluation (§6) — runs every bar.                          */
  /* ---------------------------------------------------------------- */
  const legIsUp = isUp(s.active as Column);

  if (legIsUp) {
    if (s.upPhase === 'attempt' && s.pivot.UT) {
      s.attemptExtreme = Math.max(s.attemptExtreme ?? bar.high, bar.high);
      if (!s.pivot.UT.confirmedThrough && gte(bar.high, confUpTarget(s.pivot.UT.price, cfg))) {
        signal('UPTREND_CONFIRMED', '10a', 'UT');
        s.pivot.UT.confirmedThrough = true;
        s.upPhase = 'confirmed';
      } else if (
        !s.dangerEmitted &&
        gte(s.attemptExtreme, confDownTarget(s.pivot.UT.price, cfg)) &&
        lt(s.attemptExtreme, confUpTarget(s.pivot.UT.price, cfg)) &&
        lte(bar.low, confDownTarget(s.attemptExtreme, cfg))
      ) {
        // Early 10e: a ≥C retracement from a peak that got near PP[UT] but failed.
        signal('UPTREND_DANGER', '10e', 'UT');
        s.dangerEmitted = true;
      }
    }
    // Rule 10d: downtrend declared over on a rally C beyond PP[DT] after a failed attempt.
    if (s.downPhase === 'failed' && s.pivot.DT && gte(bar.high, confUpTarget(s.pivot.DT.price, cfg))) {
      signal('DOWNTREND_OVER', '10d', 'DT');
      s.downPhase = 'over';
    }
    // Rule 9b watch: rally re-approaches PP[NR] without graduating.
    if (
      s.watchNRPending &&
      s.pivot.NR &&
      gte(bar.high, confDownTarget(s.pivot.NR.price, cfg)) &&
      lt(bar.high, confUpTarget(s.pivot.NR.price, cfg))
    ) {
      signal('WATCH_NR_PIVOT', '9b', 'NR');
      s.watchNRPending = false;
    }
  } else {
    if (s.downPhase === 'attempt' && s.pivot.DT) {
      s.attemptExtreme = Math.min(s.attemptExtreme ?? bar.low, bar.low);
      if (!s.pivot.DT.confirmedThrough && lte(bar.low, confDownTarget(s.pivot.DT.price, cfg))) {
        signal('DOWNTREND_CONFIRMED', '10c', 'DT');
        s.pivot.DT.confirmedThrough = true;
        s.downPhase = 'confirmed';
      } else if (
        !s.dangerEmitted &&
        lte(s.attemptExtreme, confUpTarget(s.pivot.DT.price, cfg)) &&
        gt(s.attemptExtreme, confDownTarget(s.pivot.DT.price, cfg)) &&
        gte(bar.high, confUpTarget(s.attemptExtreme, cfg))
      ) {
        signal('DOWNTREND_DANGER', '10f', 'DT');
        s.dangerEmitted = true;
      }
    }
    if (s.upPhase === 'failed' && s.pivot.UT && lte(bar.low, confDownTarget(s.pivot.UT.price, cfg))) {
      signal('UPTREND_OVER', '10b', 'UT');
      s.upPhase = 'over';
    }
    if (
      s.watchNRCPending &&
      s.pivot.NRC &&
      lte(bar.low, confUpTarget(s.pivot.NRC.price, cfg)) &&
      gt(bar.low, confDownTarget(s.pivot.NRC.price, cfg))
    ) {
      signal('WATCH_NRC_PIVOT', '9c', 'NRC');
      s.watchNRCPending = false;
    }
  }

  return { state: s, events };
}

/** Replay a bar sequence from a fresh (or given) state. */
export function replay(
  bars: readonly Bar[],
  cfg: EngineConfig,
  from?: LedgerState,
): { state: LedgerState; events: EngineEvent[] } {
  let state = from ?? initialState();
  const events: EngineEvent[] = [];
  for (const bar of bars) {
    const r = step(state, bar, cfg);
    state = r.state;
    events.push(...r.events);
  }
  return { state, events };
}
