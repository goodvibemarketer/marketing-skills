import {
  type Bar,
  type EngineConfig,
  type EngineEvent,
  type LedgerState,
  initialState,
  step,
} from '../src/index.js';

export const BOOK: EngineConfig = {
  swing: { value: 6, unit: 'absolute' },
  confirmation: { value: 3, unit: 'absolute' },
};

let dayCounter = 0;

/** Compact bar builder: high/low only (open/close midpoint, irrelevant to the engine). */
export function b(high: number, low = high, date?: string): Bar {
  dayCounter += 1;
  const d = date ?? `2000-01-${String(dayCounter).padStart(2, '0')}`;
  return { date: d, open: (high + low) / 2, high, low, close: (high + low) / 2 };
}

export function resetDays(): void {
  dayCounter = 0;
}

export interface RunResult {
  state: LedgerState;
  events: EngineEvent[];
  /** events grouped per input bar */
  perBar: EngineEvent[][];
}

export function run(bars: Bar[], cfg: EngineConfig = BOOK, from?: LedgerState): RunResult {
  let state = from ?? initialState();
  const events: EngineEvent[] = [];
  const perBar: EngineEvent[][] = [];
  for (const bar of bars) {
    const r = step(state, bar, cfg);
    state = r.state;
    events.push(...r.events);
    perBar.push(r.events);
  }
  return { state, events, perBar };
}

/** Sequence of {column, price} for all RECORD events. */
export function recordings(events: EngineEvent[]): Array<{ column: string; price: number; rule: string }> {
  return events
    .filter((e): e is Extract<EngineEvent, { type: 'RECORD' }> => e.type === 'RECORD')
    .map((e) => ({ column: e.column, price: e.price, rule: e.rule }));
}

export function signals(events: EngineEvent[]): Array<{ kind: string; rule: string; date: string; pivot: number }> {
  return events
    .filter((e): e is Extract<EngineEvent, { type: 'SIGNAL' }> => e.type === 'SIGNAL')
    .map((e) => ({ kind: e.kind, rule: e.rule, date: e.date, pivot: e.pivot.price }));
}

export function underlines(events: EngineEvent[]): Array<{ column: string; price: number; color: string; rule: string }> {
  return events
    .filter((e): e is Extract<EngineEvent, { type: 'UNDERLINE' }> => e.type === 'UNDERLINE')
    .map((e) => ({ column: e.column, price: e.price, color: e.color, rule: e.rule }));
}

/**
 * Standard opening: anchor at 100, rise to a UT at `top`.
 * Returns state with active = UT, last.UT = top.
 */
export function openUptrend(top = 106): RunResult {
  resetDays();
  return run([b(100), b(top)]);
}
