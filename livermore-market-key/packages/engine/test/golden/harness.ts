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
  /** Warm-start each ledger from Chart One's header entries (default true). */
  seedFromHeader?: boolean;
}

/**
 * Warm-start a ledger from Chart One's carried-forward header entries
 * (RULES.md §3, §9). The book's charts begin mid-history: the figures printed
 * above the DATE row are the pivotal points and last-recorded prices from
 * before the chart. Without this seed the engine would cold-anchor on the
 * first data row and mis-read a trend continuation as a fresh start (DD-6).
 *
 * Interpretation (top-to-bottom = oldest-to-newest within a column):
 *   - last[col] := the bottom-most header value for that column;
 *   - active    := the column that the given `firstColumn` continues;
 *   - pivot[col]:= the most recent underlined header entry for UT/DT/NR/NRC.
 * The signal phase is left conservative (`none`), so early-chart signals only
 * fire once the engine has observed a full pivot life-cycle within the charts.
 */
export function seedFromHeader(
  headerEntries: FixtureCell[],
  instrument: InstrumentKey,
  firstColumn: FixtureColumn,
): LedgerState {
  const s = initialState();
  const mine = headerEntries.filter((c) => c.instrument === instrument);
  const cols: FixtureColumn[] = ['SR', 'NR', 'UT', 'DT', 'NRC', 'SRC'];
  for (const col of cols) {
    const entries = mine.filter((c) => c.column === col);
    if (entries.length > 0) {
      s.last[col] = parsePrice(entries[entries.length - 1]!.price);
    }
    if (col === 'UT' || col === 'DT' || col === 'NR' || col === 'NRC') {
      const underlined = entries.filter((c) => c.underline !== 'none');
      const pp = underlined[underlined.length - 1];
      if (pp) {
        s.pivot[col] = {
          price: parsePrice(pp.price),
          color: pp.underlineColor === 'red' ? 'red' : 'black',
          setOn: 'header',
          confirmedThrough: false,
        };
      }
    }
  }
  // active = the column of the bottom-most (most recent) header entry: the
  // pre-chart leg the engine continues from. The first data row is frequently
  // a transition OUT of this leg (e.g. BS NR 56 7/8 → SRC 50 1/4 via rule 6h),
  // so the first *recorded* column is the wrong choice.
  s.active = mine.length > 0 ? mine[mine.length - 1]!.column : firstColumn;
  s.anchor = null;
  return s;
}

/** Replay all fixtures as one continuous series and diff against the book. */
export function replayCharts(fixtures: ChartFixture[], opts: ReplayOptions = {}): ReplayReport {
  const stockCfg = opts.stockCfg ?? BOOK_STOCK;
  const kpCfg = opts.kpCfg ?? BOOK_KP;
  const coupling = opts.coupling ?? true;

  const allRows = fixtures.flatMap((f) => f.rows);

  // Determine each instrument's first recorded column (to warm-start from the
  // Chart One header, unless the caller supplied explicit initial states).
  const firstColumnOf = (inst: InstrumentKey): FixtureColumn | null => {
    for (const row of allRows) {
      const cell = row.cells.find((c) => c.instrument === inst);
      if (cell) return cell.column;
    }
    return null;
  };

  const header = fixtures.find((f) => f.chart === 1)?.headerEntries ?? [];
  const seed = (inst: InstrumentKey): LedgerState => {
    if (opts.initialStates?.[inst]) return opts.initialStates[inst]!;
    if (opts.seedFromHeader === false) return initialState();
    const fc = firstColumnOf(inst);
    if (!fc || header.length === 0) return initialState();
    return seedFromHeader(header, inst, fc);
  };

  const states: Record<InstrumentKey, LedgerState> = {
    US: seed('US'),
    BS: seed('BS'),
    KP: seed('KP'),
  };
  const events: Record<InstrumentKey, EngineEvent[]> = { US: [], BS: [], KP: [] };
  const mismatches: Mismatch[] = [];
  const known = fixtures.flatMap((f) => f.knownDivergences ?? []);
  let totalEntries = 0;
  let matchedEntries = 0;


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
