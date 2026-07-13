/**
 * Golden-master harness (Phase 3): replays the book's own charts
 * (pp. 102–133, March 1938 – February 1940) through the engine in
 * fixed-point mode (6/3/12) and compares cell-by-cell.
 *
 * Input convention (RULES.md §9): each charted figure is the day's extreme,
 * so the replay bar for a recorded day is {high = low = price}; blank days
 * contribute no bar. The Key Price ledger replays the book's own KP figures.
 */
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import {
  type Bar,
  type CouplingHints,
  type EngineConfig,
  type EngineEvent,
  type LedgerState,
  initialState,
  isUp,
  parsePrice,
  step,
} from '../../src/index.js';

export type InstrumentKey = 'US' | 'BS' | 'KP';
export type FixtureColumn = 'SR' | 'NR' | 'UT' | 'DT' | 'NRC' | 'SRC';

export interface FixtureCell {
  instrument: InstrumentKey;
  column: FixtureColumn;
  price: string;
  ink: 'black' | 'red' | 'blue';
  underline: 'none' | 'single' | 'double';
  underlineColor?: 'black' | 'red' | 'mixed' | 'none';
  uncertain?: boolean;
  note?: string;
}

export interface FixtureRow {
  date: string;
  dateLabel: string;
  cells: FixtureCell[];
}

export interface FixtureAnnotation {
  text: string;
  ruleRefs?: string[];
  correctedRuleRefs?: string[];
  dateRefs?: string[];
}

export interface KnownDivergence {
  date: string;
  instrument: InstrumentKey;
  kind: 'book-extra-entry' | 'engine-extra-entry' | 'column-differs' | 'underline-differs' | 'signal-differs';
  reason: string;
}

export interface ChartFixture {
  chart: number;
  bookPages: [number, number];
  headerEntries: FixtureCell[];
  rows: FixtureRow[];
  annotations: FixtureAnnotation[];
  knownDivergences?: KnownDivergence[];
  notes?: string;
}

export const BOOK_STOCK: EngineConfig = {
  swing: { value: 6, unit: 'absolute' },
  confirmation: { value: 3, unit: 'absolute' },
};

export const BOOK_KP: EngineConfig = {
  swing: { value: 12, unit: 'absolute' },
  confirmation: { value: 6, unit: 'absolute' },
};

export function loadFixtures(dir: string): ChartFixture[] {
  const files = readdirSync(dir)
    .filter((f) => /^chart-\d+\.json$/.test(f))
    .sort((a, b) => Number(a.match(/\d+/)![0]) - Number(b.match(/\d+/)![0]));
  return files.map((f) => JSON.parse(readFileSync(join(dir, f), 'utf8')) as ChartFixture);
}

export interface Mismatch {
  date: string;
  instrument: InstrumentKey;
  kind: KnownDivergence['kind'];
  detail: string;
}

export interface ReplayReport {
  mismatches: Mismatch[];
  /** true mismatches not covered by knownDivergences */
  unexplained: Mismatch[];
  totalEntries: number;
  matchedEntries: number;
  events: Record<InstrumentKey, EngineEvent[]>;
  finalStates: Record<InstrumentKey, LedgerState>;
}

export interface ReplayOptions {
  stockCfg?: EngineConfig;
  kpCfg?: EngineConfig;
  /** Coupling: relax member thresholds when the book KP ledger recorded that day (DD-13). */
  coupling?: boolean;
  initialStates?: Partial<Record<InstrumentKey, LedgerState>>;
}

/** Replay all fixtures as one continuous series and diff against the book. */
export function replayCharts(fixtures: ChartFixture[], opts: ReplayOptions = {}): ReplayReport {
  const stockCfg = opts.stockCfg ?? BOOK_STOCK;
  const kpCfg = opts.kpCfg ?? BOOK_KP;
  const coupling = opts.coupling ?? true;

  const states: Record<InstrumentKey, LedgerState> = {
    US: opts.initialStates?.US ?? initialState(),
    BS: opts.initialStates?.BS ?? initialState(),
    KP: opts.initialStates?.KP ?? initialState(),
  };
  const events: Record<InstrumentKey, EngineEvent[]> = { US: [], BS: [], KP: [] };
  const mismatches: Mismatch[] = [];
  const known = fixtures.flatMap((f) => f.knownDivergences ?? []);
  let totalEntries = 0;
  let matchedEntries = 0;

  const allRows = fixtures.flatMap((f) => f.rows);

  for (const row of allRows) {
    const byInstrument = new Map<InstrumentKey, FixtureCell[]>();
    for (const c of row.cells) {
      const list = byInstrument.get(c.instrument) ?? [];
      list.push(c);
      byInstrument.set(c.instrument, list);
    }

    // KP first (self-contained), then members with coupling hints.
    const dayEvents: Partial<Record<InstrumentKey, EngineEvent[]>> = {};
    let hints: CouplingHints | undefined;

    const kpCells = byInstrument.get('KP');
    if (kpCells && kpCells.length > 0) {
      const price = parsePrice(kpCells[0]!.price);
      const bar: Bar = { date: row.date, open: price, high: price, low: price, close: price };
      const r = step(states.KP, bar, kpCfg);
      states.KP = r.state;
      events.KP.push(...r.events);
      dayEvents.KP = r.events;
      if (coupling) {
        let up = false;
        let down = false;
        for (const e of r.events) {
          if (e.type === 'RECORD') {
            if (isUp(e.column)) up = true;
            else down = true;
          }
        }
        hints = { kpRecordedUp: up, kpRecordedDown: down };
      }
    }

    for (const inst of ['US', 'BS'] as const) {
      const cells = byInstrument.get(inst);
      if (!cells || cells.length === 0) continue;
      const price = parsePrice(cells[0]!.price);
      const bar: Bar = { date: row.date, open: price, high: price, low: price, close: price };
      const r = step(states[inst], bar, stockCfg, hints);
      states[inst] = r.state;
      events[inst].push(...r.events);
      dayEvents[inst] = r.events;
    }

    // Diff: every fixture cell should have a matching RECORD event.
    for (const [inst, cells] of byInstrument) {
      for (const cell of cells) {
        totalEntries += 1;
        const recs = (dayEvents[inst] ?? []).filter(
          (e): e is Extract<EngineEvent, { type: 'RECORD' }> => e.type === 'RECORD',
        );
        if (recs.length === 0) {
          mismatches.push({
            date: row.date,
            instrument: inst,
            kind: 'book-extra-entry',
            detail: `book records ${cell.price} in ${cell.column}; engine records nothing`,
          });
        } else if (recs[0]!.column !== cell.column) {
          mismatches.push({
            date: row.date,
            instrument: inst,
            kind: 'column-differs',
            detail: `book: ${cell.column} ${cell.price}; engine: ${recs[0]!.column} (rule ${recs[0]!.rule})`,
          });
        } else {
          matchedEntries += 1;
        }
      }
    }
  }

  const unexplained = mismatches.filter(
    (m) => !known.some((k) => k.date === m.date && k.instrument === m.instrument && k.kind === m.kind),
  );

  return { mismatches, unexplained, totalEntries, matchedEntries, events, finalStates: states };
}

/** Pretty-print mismatches for the fitting loop. */
export function formatMismatches(ms: Mismatch[]): string {
  return ms.map((m) => `  ${m.date} ${m.instrument} [${m.kind}] ${m.detail}`).join('\n');
}
