/**
 * Core types for the Livermore Market Key rule engine.
 * See RULES.md at the repository root for the formal specification;
 * spec cross-references appear as (§n) and (DD-n).
 */

export type Column = 'SR' | 'NR' | 'UT' | 'DT' | 'NRC' | 'SRC';

export const UP_COLUMNS: readonly Column[] = ['SR', 'NR', 'UT'];
export const DOWN_COLUMNS: readonly Column[] = ['DT', 'NRC', 'SRC'];

export function isUp(col: Column): boolean {
  return col === 'SR' || col === 'NR' || col === 'UT';
}

export type Ink = 'black' | 'red' | 'pencil';

/** Ink convention, book rules 1–3 (§1). */
export function inkFor(col: Column): Ink {
  if (col === 'UT') return 'black';
  if (col === 'DT') return 'red';
  return 'pencil';
}

/** A completed daily OHLC bar. Dates are ISO `YYYY-MM-DD` strings. */
export interface Bar {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

/** Threshold with explicit unit (§8). Percent values are in percent, e.g. `{ value: 6, unit: 'percent' }` = 6%. */
export interface Threshold {
  value: number;
  unit: 'absolute' | 'percent';
}

export interface EngineConfig {
  /** Swing threshold S — "approximately six points" (book), e.g. `{value: 6, unit: 'absolute'}`. */
  swing: Threshold;
  /** Confirmation margin C — "three points" (book). Invariant C = S/2 is the caller's responsibility. */
  confirmation: Threshold;
  /**
   * Tolerance subtracted from the swing threshold value, in the same unit (DD-2).
   * Default 0 (strict). Book-replay mode may use a small tolerance to match
   * Livermore's hand-rounded "approximately".
   */
  swingTolerance?: number;
}

/**
 * Commitment level of a column on one side of the ledger (§12): the up side is
 * `SR`(1) < `NR`(2) < `UT`(3); the down side mirrors `SRC`(1) < `NRC`(2) < `DT`(3).
 */
export type Commitment = 1 | 2 | 3;

/** Cross-ledger coupling hints for Key Price group members (§7, DD-13, §12). */
export interface CouplingHints {
  /** The group's Key Price ledger recorded an up-direction figure today (DD-13). */
  kpRecordedUp: boolean;
  /** The group's Key Price ledger recorded a down-direction figure today (DD-13). */
  kpRecordedDown: boolean;
  /**
   * Key Price group-confirmation cap (§12). The member may commit no further up
   * the up-side ladder than the Key Price itself: 1 = only `SR`, 2 = up to `NR`,
   * 3 = up to `UT`. Omitted for ungrouped instruments (no cap).
   */
  kpUpCap?: Commitment;
  /** Key Price confirmation cap on the down side: 1 = only `SRC`, 2 = to `NRC`, 3 = to `DT`. */
  kpDownCap?: Commitment;
}

/** Up-side commitment level of a column, or 0 if it is a down-side column. */
export function upLevel(col: Column): 0 | Commitment {
  return col === 'SR' ? 1 : col === 'NR' ? 2 : col === 'UT' ? 3 : 0;
}

/** Down-side commitment level of a column, or 0 if it is an up-side column. */
export function downLevel(col: Column): 0 | Commitment {
  return col === 'SRC' ? 1 : col === 'NRC' ? 2 : col === 'DT' ? 3 : 0;
}

/** The Key Price's active column → the caps it imposes on members (§12). */
export function capsFromKeyPriceColumn(active: Column | null): { up: Commitment; down: Commitment } {
  return {
    up: active === 'UT' ? 3 : active === 'NR' ? 2 : 1,
    down: active === 'DT' ? 3 : active === 'NRC' ? 2 : 1,
  };
}

export interface PivotalPoint {
  price: number;
  color: 'red' | 'black';
  setOn: string;
  /** True once price has carried through by C (rule 10a). */
  confirmedThrough: boolean;
}

/** Life-cycle of the "is the trend intact?" question per side (§6). */
export type TrendPhase =
  | 'none'
  | 'firstCounter'
  | 'attempt'
  | 'failed'
  | 'confirmed'
  | 'over';

export interface LedgerState {
  /** Column currently being recorded; null before the ledger anchors (DD-6). */
  active: Column | null;
  /** Last recorded price per column. */
  last: Record<Column, number | null>;
  /** Pivotal points — the underlined figures (rules 4 & 8, §5). */
  pivot: {
    UT: PivotalPoint | null;
    DT: PivotalPoint | null;
    NR: PivotalPoint | null;
    NRC: PivotalPoint | null;
  };
  /** Signal-phase tracking, up side (PP[UT] life-cycle). */
  upPhase: TrendPhase;
  /** Signal-phase tracking, down side (PP[DT] life-cycle). */
  downPhase: TrendPhase;
  /** Extreme of the current leg's attempt toward PP (for rules 10e/10f). */
  attemptExtreme: number | null;
  /** 10e/10f danger already emitted for the current attempt. */
  dangerEmitted: boolean;
  /** 9b/9c watch pending: PP[NR]/PP[NRC] set and the "next" counter-leg has not yet entered the watch window. */
  watchNRPending: boolean;
  watchNRCPending: boolean;
  /** Pre-anchor running extremes (DD-6). */
  anchor: { hi: number; hiDate: string; lo: number; loDate: string } | null;
  /**
   * Direction of the last trend-column entry ('up' = last recorded UT,
   * 'down' = last recorded DT). Used by the §12 Key Price confirmation cap,
   * which gates only *counter-trend* moves (a rally against a downtrend, or a
   * reaction against an uptrend) — with-trend continuations never need
   * confirmation. Null before any trend column has been recorded.
   */
  lastTrendDir: 'up' | 'down' | null;
}

/* ------------------------------------------------------------------ */
/* Events                                                              */
/* ------------------------------------------------------------------ */

export interface RecordEvent {
  type: 'RECORD';
  date: string;
  column: Column;
  price: number;
  ink: Ink;
  /** Book rule that produced the recording, e.g. '6c', '5a', '6f-continuation'. */
  rule: string;
}

export interface UnderlineEvent {
  type: 'UNDERLINE';
  date: string;
  column: Column;
  price: number;
  color: 'red' | 'black';
  /** '4a' | '4b' | '4c' | '4d' */
  rule: string;
}

export interface PivotSetEvent {
  type: 'PIVOT_SET';
  date: string;
  column: 'UT' | 'DT' | 'NR' | 'NRC';
  price: number;
}

export type SignalKind =
  | 'UPTREND_CONFIRMED'   // 10a (up)
  | 'DOWNTREND_CONFIRMED' // 10c
  | 'UPTREND_OVER'        // 10b
  | 'DOWNTREND_OVER'      // 10d
  | 'UPTREND_DANGER'      // 10e
  | 'DOWNTREND_DANGER'    // 10f
  | 'BUY_WATCH'           // 9a
  | 'SELL_WATCH'          // 9c (mirror of 9a)
  | 'WATCH_NR_PIVOT'      // 9b
  | 'WATCH_NRC_PIVOT';    // 9c (mirror of 9b)

export interface SignalEvent {
  type: 'SIGNAL';
  date: string;
  kind: SignalKind;
  /** Book rule reference, e.g. '10a', '10f'. */
  rule: string;
  /** The pivotal point the signal refers to. */
  pivot: { column: 'UT' | 'DT' | 'NR' | 'NRC'; price: number };
}

export type EngineEvent = RecordEvent | UnderlineEvent | PivotSetEvent | SignalEvent;

export interface StepResult {
  state: LedgerState;
  events: EngineEvent[];
}

export function initialState(): LedgerState {
  return {
    active: null,
    last: { SR: null, NR: null, UT: null, DT: null, NRC: null, SRC: null },
    pivot: { UT: null, DT: null, NR: null, NRC: null },
    upPhase: 'none',
    downPhase: 'none',
    attemptExtreme: null,
    dangerEmitted: false,
    watchNRPending: false,
    watchNRCPending: false,
    anchor: null,
    lastTrendDir: null,
  };
}
