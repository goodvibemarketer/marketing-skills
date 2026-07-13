/**
 * Per-rule unit tests (Phase 3 item 3): rules 4a–d, 5a–b, 6a–h, 7, 8, 9a–c, 10a–f
 * as formalized in RULES.md. Absolute 6/3 thresholds (book mode).
 */
import { describe, expect, it } from 'vitest';
import { BOOK, b, openUptrend, recordings, resetDays, run, signals, underlines } from './helpers.js';
import { initialState, step, stepGroup, initialGroupState, keyPriceBar, parsePrice, formatPrice } from '../src/index.js';

describe('anchoring (DD-6)', () => {
  it('opens UT on the first 6-point rally from the running low', () => {
    resetDays();
    const r = run([b(100), b(103), b(106.5)]);
    expect(recordings(r.events)).toEqual([{ column: 'UT', price: 106.5, rule: 'anchor-up (DD-6)' }]);
  });
  it('opens DT on the first 6-point reaction from the running high', () => {
    resetDays();
    const r = run([b(100), b(98), b(94, 93.5)]);
    expect(recordings(r.events)).toEqual([{ column: 'DT', price: 93.5, rule: 'anchor-down (DD-6)' }]);
  });
  it('does not record before a full swing accrues', () => {
    resetDays();
    const r = run([b(100), b(104), b(99.5)]);
    expect(recordings(r.events)).toEqual([]);
    expect(r.state.active).toBeNull();
  });
});

describe('recording the daily extreme, not the close (DD-4)', () => {
  it('records the high in up columns and the low in down columns', () => {
    resetDays();
    const r = run([b(100), b(107, 104)]); // wide day: high 107 anchors UT
    expect(recordings(r.events)).toEqual([{ column: 'UT', price: 107, rule: 'anchor-up (DD-6)' }]);
  });
});

describe('rule 6a + 4a: reaction from Upward Trend → Natural Reaction', () => {
  it('moves recording to NRC on a 6-point reaction and draws red lines under last UT (pivotal point)', () => {
    const o = openUptrend(106);
    const r = run([b(100.5, 100)], BOOK, o.state); // 106 − 6 = 100
    expect(recordings(r.events)).toEqual([{ column: 'NRC', price: 100, rule: '6a' }]);
    expect(underlines(r.events)).toEqual([{ column: 'UT', price: 106, color: 'red', rule: '4a' }]);
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'SELL_WATCH', rule: '9c', pivot: 106 }));
  });
  it('does not fire at 5.99 points (strict >=, DD-1)', () => {
    const o = openUptrend(106);
    const r = run([b(100.5, 100.01)], BOOK, o.state);
    expect(recordings(r.events)).toEqual([]);
  });
  it('continues recording lower lows in NRC (rule 6a continuation)', () => {
    const o = openUptrend(106);
    const r = run([b(100.5, 100), b(99.5, 99)], BOOK, o.state);
    expect(recordings(r.events).map((x) => x.price)).toEqual([100, 99]);
  });
});

describe('rule 6c + 4c + 9a: rally from Downward Trend → Natural Rally', () => {
  it('moves recording to NR, draws black lines under last DT, emits BUY_WATCH', () => {
    resetDays();
    const o = run([b(100), b(94, 93)]); // anchor DT at 93
    const r = run([b(99, 98)], BOOK, o.state); // 93 + 6 = 99
    expect(recordings(r.events)).toEqual([{ column: 'NR', price: 99, rule: '6c' }]);
    expect(underlines(r.events)).toEqual([{ column: 'DT', price: 93, color: 'black', rule: '4c' }]);
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'BUY_WATCH', rule: '9a', pivot: 93 }));
  });
  it('overwrites a stale higher NR value (Chart One behavior: 62 7/8 → 43 1/2)', () => {
    resetDays();
    // Build: UT 106 → NRC 100 → NR 105 (via 6d) → NRC 99 → DT 93* → rally
    const o = run([b(100), b(106), b(100.25, 100), b(105), b(99, 98.8)]);
    // state: last.NR = 105; reaction from NR 105 to 98.8 → NRC (lower than last NRC 100)
    const r1 = run([b(92.5, 92)], BOOK, o.state); // continuation NRC → 92... then DT? last.DT null → stays NRC
    const r2 = run([b(98.5, 98)], BOOK, r1.state); // rally 92 + 6 = 98 → NR overwrite (98 < last.NR 105)
    const recs = recordings(r2.events);
    expect(recs).toEqual([{ column: 'NR', price: 98.5, rule: '6d' }]);
    expect(r2.state.last.NR).toBe(98.5);
  });
});

describe('rule 6b + 4d: reaction from Natural Rally', () => {
  it('routes to NRC when lower than last NRC, drawing black lines under last NR', () => {
    resetDays();
    const o = run([b(100), b(106), b(100.25, 100), b(106, 105.8)]); // UT 106, NRC 100, NR 106
    const r = run([b(99, 98.9)], BOOK, o.state); // 106 − 6 = 100 ≥ 98.9; 98.9 < last NRC 100 → NRC
    expect(recordings(r.events)).toEqual([{ column: 'NRC', price: 98.9, rule: '6b' }]);
    expect(underlines(r.events)).toEqual([{ column: 'NR', price: 106, color: 'black', rule: '4d' }]);
  });
  it('6b tail: goes straight to DT in red ink when the price undercuts last DT', () => {
    resetDays();
    const o = run([b(100), b(94, 93.9), b(100, 99.9)]); // DT 93.9 → NR 100 (via 6c)
    const r = run([b(93, 92)], BOOK, o.state); // reaction 8 from 100; 92 < last DT 93.9 → DT
    const recs = recordings(r.events);
    expect(recs).toEqual([{ column: 'DT', price: 92, rule: expect.stringContaining('6b-tail') }]);
  });
});

describe('rule 6d: rally from Natural Reaction', () => {
  it('routes to NR when higher than last NR, drawing red lines under last NRC (4b)', () => {
    resetDays();
    const o = run([b(100), b(106), b(100.25, 100)]); // UT 106 → NRC 100
    const r = run([b(106 - 0.5, 105)], BOOK, o.state); // 100 + 6 = 106 > high 105.5 → not yet
    expect(recordings(r.events)).toEqual([]);
    const r2 = run([b(106.0001 - 0.0001, 105.9)], BOOK, o.state); // high 106 ≥ 106 → NR? but 106 !> last.UT 106
    expect(recordings(r2.events)).toEqual([{ column: 'NR', price: 106, rule: '6d' }]);
    expect(underlines(r2.events)).toEqual([{ column: 'NRC', price: 100, color: 'red', rule: '4b' }]);
  });
  it('6d tail: goes straight to UT in black ink when the price exceeds last UT', () => {
    resetDays();
    const o = run([b(100), b(106), b(100.25, 100)]);
    const r = run([b(107, 106.5)], BOOK, o.state); // 100+6=106; 107 > last UT 106 → UT
    expect(recordings(r.events)).toEqual([{ column: 'UT', price: 107, rule: expect.stringContaining('6d-tail') }]);
  });
});

describe('rule 6e / 6f: piercing the trend column from a natural column', () => {
  it('6f: recording in NR, a price above last UT is entered in UT (black ink)', () => {
    resetDays();
    const o = run([b(100), b(106), b(99.5, 99), b(105.2, 105)]); // UT 106 → NRC 99 → NR 105.2
    expect(o.state.active).toBe('NR');
    const r = run([b(106.5, 106)], BOOK, o.state);
    expect(recordings(r.events)).toEqual([{ column: 'UT', price: 106.5, rule: '6f' }]);
  });
  it('6e: recording in NRC, a price below last DT is entered in DT (red ink)', () => {
    resetDays();
    const o = run([b(100), b(94, 93.9), b(100, 99.9), b(94.5, 94)]); // DT 93.9 → NR 100 → NRC 94 (6b: 94 < ... null NRC → NRC)
    const r = run([b(93.5, 93)], BOOK, o.state); // 93 < last DT 93.9 → DT
    expect(recordings(r.events)).toEqual([{ column: 'DT', price: 93, rule: '6e' }]);
  });
});

describe('rule 6g: Secondary Rally', () => {
  it('routes a 6-point rally that fails to exceed last NR into SR, then resumes NR when exceeded', () => {
    resetDays();
    // UT 112 → NRC 100 (12-pt reaction) → NR 106 (6d) → NRC 98 (6b, lower than 100) → rally to 105 (< last NR 106) → SR
    const o = run([b(100), b(112), b(100.5, 100), b(106), b(98.5, 98)]);
    const r = run([b(104.5, 104)], BOOK, o.state); // 98 + 6 = 104 ≤ 104.5, but 104.5 < last NR 106 → SR
    expect(recordings(r.events)).toEqual([{ column: 'SR', price: 104.5, rule: '6g' }]);
    // A rally routing to Secondary Rally draws NO 4b underline under NRC — rule
    // 4b fires only on a rally into Natural Rally or Upward Trend (DD-9/DD-19).
    expect(underlines(r.events).filter((u) => u.column === 'NRC')).toHaveLength(0);
    const r2 = run([b(106.5, 106.2)], BOOK, r.state); // exceeds last NR 106 → resume NR
    expect(recordings(r2.events)).toEqual([{ column: 'NR', price: 106.5, rule: '6g-resume' }]);
  });
});

describe('rule 6h: Secondary Reaction', () => {
  it('routes a 6-point reaction that stays above last NRC into SRC, then resumes NRC when undercut', () => {
    resetDays();
    // DT 88 → NR 100 (6c, 12pt) → NRC 94 (6b) → NR 100.25?? — instead: NRC 94, rally 100 (6d: 100 !> last NR 100 → ... careful)
    // Build: anchor DT 88, NR 100, reaction to 94 → NRC 94 (4d under NR 100), rally to 100.5 → NR 100.5 (6d),
    // then reaction to 94.5: ≥6, but 94.5 > last NRC 94 → SRC.
    const o = run([b(100), b(94, 88), b(100, 99.5), b(94.5, 94), b(100.5, 100.2)]);
    const r = run([b(95, 94.5)], BOOK, o.state); // 100.5 − 6 = 94.5; 94.5 > last NRC 94 → SRC
    expect(recordings(r.events)).toEqual([{ column: 'SRC', price: 94.5, rule: '6h' }]);
    const r2 = run([b(94, 93.8)], BOOK, r.state); // 93.8 < last NRC 94 → resume NRC
    expect(recordings(r2.events)).toEqual([{ column: 'NRC', price: 93.8, rule: '6h-resume' }]);
  });
});

describe('rule 5a: graduation from Natural Rally into Upward Trend at PP[NR] + 3', () => {
  it('enters UT in black ink even when below last UT', () => {
    resetDays();
    // UT 120 → NRC 100 → NR 106 (6d) → NRC 99 (6b; 4d underlines NR 106 → PP[NR] = 106)
    const o = run([b(100), b(120), b(100.5, 100), b(106), b(99.5, 99)]);
    // rally: 99 + 6 = 105 → NR? no: 6d requires > last NR 106 → 105.5 → SR... use 106.5:
    // 106.5 > last NR 106 → NR; then continuation to 108.9 < 109 = PP+3: still NR; at 109 → UT (5a), below last UT 120.
    const r1 = run([b(106.5, 106)], BOOK, o.state);
    expect(recordings(r1.events)).toEqual([{ column: 'NR', price: 106.5, rule: '6d' }]);
    const r2 = run([b(108.9, 108)], BOOK, r1.state);
    expect(recordings(r2.events)).toEqual([{ column: 'NR', price: 108.9, rule: '6-continuation' }]);
    const r3 = run([b(109, 108.5)], BOOK, r2.state);
    expect(recordings(r3.events)).toEqual([{ column: 'UT', price: 109, rule: '5a' }]);
  });
});

describe('rule 5b: graduation from Natural Reaction into Downward Trend at PP[NRC] − 3', () => {
  it('enters DT in red ink even when above last DT', () => {
    resetDays();
    // DT 80 → NR 100 (6c) → NRC 94 (6b; last NRC null) → NR 100.5 → NRC 94.5?? > 94 → SRC... build carefully:
    // DT 80, NR 100, NRC 94 (PP[NR]=100 via 4d), rally 100.5 (6d > 100) → 4b underlines NRC 94 → PP[NRC] = 94.
    // reaction from 100.5 to 94.2 (> 94 → SRC), continue down: 91 ≤ PP[NRC] − 3 = 91 → DT (5b), above last DT 80.
    const o = run([b(100), b(86, 80), b(100, 99), b(94.5, 94), b(100.5, 100.2)]);
    const r1 = run([b(94.6, 94.2)], BOOK, o.state);
    expect(recordings(r1.events)).toEqual([{ column: 'SRC', price: 94.2, rule: '6h' }]);
    const r2 = run([b(91.5, 91)], BOOK, r1.state);
    expect(recordings(r2.events)).toEqual([{ column: 'DT', price: 91, rule: '5b' }]);
  });
});

describe('rule 8: pivotal points', () => {
  it('sets PP on the trend column when a counter-swing begins, and on the natural column when it ends', () => {
    resetDays();
    const o = run([b(100), b(106), b(100.25, 100), b(106, 105.8)]); // UT 106 → NRC 100 → NR 106
    expect(o.state.pivot.UT).toMatchObject({ price: 106, color: 'red' });
    expect(o.state.pivot.NRC).toMatchObject({ price: 100, color: 'red' });
    const r = run([b(99.5, 99.4)], BOOK, o.state); // leaves NR 106 → PP[NR]
    expect(r.state.pivot.NR).toMatchObject({ price: 106, color: 'black' });
  });
});

describe('rule 10a: trend resumption confirmation (carry-through by 3)', () => {
  it('emits UPTREND_CONFIRMED when a rally carries 3 through PP[UT]', () => {
    resetDays();
    const o = run([b(100), b(106), b(100.25, 100), b(106.2, 106)]); // NRC 100, rally → 106.2 > last UT 106 → UT (6d tail)
    // upPhase became 'attempt' on the up-transition; 106.2 < 109 not confirmed yet
    const r = run([b(109, 108.5)], BOOK, o.state);
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'UPTREND_CONFIRMED', rule: '10a', pivot: 106 }));
  });
  it('emits DOWNTREND_CONFIRMED when a reaction carries 3 through PP[DT] (rule 10c)', () => {
    resetDays();
    const o = run([b(100), b(94, 93), b(99, 98.5)]); // DT 93 → NR 99 (PP[DT] = 93)
    const r = run([b(93.5, 90)], BOOK, o.state); // reaction from 99 to 90 ≤ 93 − 3 = 90 → DT (6b tail: 90 < 93) + confirm
    expect(recordings(r.events)).toEqual([{ column: 'DT', price: 90, rule: expect.stringContaining('6b-tail') }]);
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'DOWNTREND_CONFIRMED', rule: '10c', pivot: 93 }));
  });
});

describe('rules 10b/10e: failed rally near PP[UT]', () => {
  function failedRallySetup() {
    resetDays();
    // UT 109 → reaction to 100 (NRC, PP[UT]=109) → rally to 107 (6d, in window [106,112)) → attempt
    return run([b(100), b(109), b(100.5, 100), b(107, 106.5)]);
  }
  it('10e: danger when the rally dies within 3 of the PP and retraces 3', () => {
    const o = failedRallySetup();
    const r = run([b(104.5, 104)], BOOK, o.state); // low 104 ≤ 107 − 3 → early danger
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'UPTREND_DANGER', rule: '10e', pivot: 109 }));
  });
  it('10b: uptrend over when, after the failed attempt, price sells 3 below the PP', () => {
    const o = failedRallySetup();
    const r = run([b(101.5, 101)], BOOK, o.state); // swing down 107−6=101 → NRC leg (failed) ... 101 > 109−3=106? no: 101 ≤ 106 → also 10b
    const sigs = signals(r.events).map((s) => s.kind);
    expect(sigs).toContain('UPTREND_DANGER'); // final 10e on leg end (peak 107 in window)
    expect(sigs).toContain('UPTREND_OVER'); // 10b: low 101 ≤ 106
  });
  it('no 10e when the rally never got near the PP', () => {
    resetDays();
    const o = run([b(100), b(109), b(100.5, 100), b(105.9, 105.5)]); // peak 105.9 < 106 = PP−3 → outside window
    const r = run([b(99.8, 99.5)], BOOK, o.state); // leg ends (105.9 − 6 = 99.9 ≥ 99.5)
    const sigs = signals(r.events).map((s) => s.kind);
    expect(sigs).not.toContain('UPTREND_DANGER');
  });
});

describe('rules 10d/10f: failed reaction near PP[DT]', () => {
  function failedReactionSetup() {
    resetDays();
    // DT 91 → rally to 100 (NR, PP[DT]=91) → reaction to 93 (6b→NRC; trough in window (88, 94])
    return run([b(100), b(97, 91), b(100, 99.5), b(93.5, 93)]);
  }
  it('10f: danger when the reaction ends a short distance above the PP and rallies 3', () => {
    const o = failedReactionSetup();
    const r = run([b(96, 95.5)], BOOK, o.state); // high 96 ≥ 93 + 3 → early 10f
    expect(signals(r.events)).toContainEqual(expect.objectContaining({ kind: 'DOWNTREND_DANGER', rule: '10f', pivot: 91 }));
  });
  it('10d: downtrend over when, after the failed attempt, price rallies 3 above the PP', () => {
    const o = failedReactionSetup();
    const r = run([b(99, 98.5)], BOOK, o.state); // swing up 93+6=99 → NR leg (failed) ... high 99 ≥ 91+3=94 → 10d
    const sigs = signals(r.events).map((s) => s.kind);
    expect(sigs).toContain('DOWNTREND_DANGER');
    expect(sigs).toContain('DOWNTREND_OVER');
  });
});

describe('rule 9b: watch when a later rally re-approaches PP[NR]', () => {
  it('emits WATCH_NR_PIVOT inside [PP−3, PP+3)', () => {
    resetDays();
    // UT 120 → NRC 106 → NR 112 (6d) → NRC 104 (6b, above PP[NRC]−3 → no 5b; 4d → PP[NR]=112, watch pending)
    const o = run([b(100), b(120), b(106.5, 106), b(112), b(104.5, 104)]);
    expect(o.state.pivot.NR).toMatchObject({ price: 112 });
    // rally from 104: swing at 110 → SR (110 < last NR 112), already inside window [109, 115)
    const r1 = run([b(110, 109.5)], BOOK, o.state);
    expect(recordings(r1.events).at(0)?.column).toBe('SR');
    expect(signals(r1.events)).toContainEqual(expect.objectContaining({ kind: 'WATCH_NR_PIVOT', rule: '9b', pivot: 112 }));
  });
});

describe('rule 7: Key Price uses a 12-point basis (group)', () => {
  const groupCfg = {
    member: BOOK,
    keyPrice: { swing: { value: 12, unit: 'absolute' }, confirmation: { value: 6, unit: 'absolute' } },
    coupling: true,
    method: 'sum',
  } as const;

  it('KP bar is the sum of member bars; KP ledger swings on 12', () => {
    const kp = keyPriceBar(
      { date: 'd', open: 50, high: 51, low: 49, close: 50 },
      { date: 'd', open: 40, high: 42, low: 39, close: 41 },
      groupCfg,
    );
    expect(kp.high).toBe(93);
    expect(kp.low).toBe(88);
  });

  it('DD-13 coupling: a member records on a sub-6 move when the Key Price swings 12', () => {
    let gs = initialGroupState();
    const day = (dateNum: number, aHi: number, aLo: number, bHi: number, bLo: number) => {
      const date = `2000-02-${String(dateNum).padStart(2, '0')}`;
      const bars = {
        a: { date, open: aHi, high: aHi, low: aLo, close: aLo },
        b: { date, open: bHi, high: bHi, low: bLo, close: bLo },
      };
      const r = stepGroup(gs, bars, groupCfg);
      gs = r.state;
      return r.events;
    };
    day(1, 50, 50, 50, 50); // anchors
    day(2, 57, 56.5, 57, 56.5); // both UT (7-pt rallies; KP 114 = 14-pt → KP UT)
    // reaction: member A only 5.5 (sub-6), member B 7 → KP 12.5 → all three record
    const ev = day(3, 52, 51.5, 51, 50);
    const aRecs = ev.a.filter((e) => e.type === 'RECORD');
    const bRecs = ev.b.filter((e) => e.type === 'RECORD');
    const kpRecs = ev.kp.filter((e) => e.type === 'RECORD');
    expect(kpRecs).toHaveLength(1);
    expect(kpRecs[0]).toMatchObject({ column: 'NRC', price: 101.5 });
    expect(bRecs).toHaveLength(1);
    expect(bRecs[0]).toMatchObject({ column: 'NRC', price: 50 });
    expect(aRecs).toHaveLength(1); // 5.5 < 6 alone, but KP coupling pulls it in
    expect(aRecs[0]).toMatchObject({ column: 'NRC', price: 51.5 });
    expect((aRecs[0] as { rule: string }).rule).toContain('DD-13');
  });

  it('without coupling the sub-6 member does not record', () => {
    let gs = initialGroupState();
    const cfg = { ...groupCfg, coupling: false } as const;
    const day = (dateNum: number, aHi: number, aLo: number, bHi: number, bLo: number) => {
      const date = `2000-03-${String(dateNum).padStart(2, '0')}`;
      const bars = {
        a: { date, open: aHi, high: aHi, low: aLo, close: aLo },
        b: { date, open: bHi, high: bHi, low: bLo, close: bLo },
      };
      const r = stepGroup(gs, bars, cfg);
      gs = r.state;
      return r.events;
    };
    day(1, 50, 50, 50, 50);
    day(2, 57, 56.5, 57, 56.5);
    const ev = day(3, 52, 51.5, 51, 50);
    expect(ev.a.filter((e) => e.type === 'RECORD')).toHaveLength(0);
    expect(ev.b.filter((e) => e.type === 'RECORD')).toHaveLength(1);
  });
});

describe('DD-3: one figure per day; continuation beats reversal on a wide bar', () => {
  it('records the same-direction extreme and defers the counter-swing', () => {
    const o = openUptrend(106);
    // wide day: new high 108 AND low 101 (7 below the NEW high, 5 below the old)
    const r = run([b(108, 101)], BOOK, o.state);
    expect(recordings(r.events)).toEqual([{ column: 'UT', price: 108, rule: '6-continuation' }]);
    // next day the reaction persists → transition measured from updated extreme 108
    const r2 = run([b(102.5, 102)], BOOK, r.state);
    expect(recordings(r2.events)).toEqual([{ column: 'NRC', price: 102, rule: '6a' }]);
  });
});

describe('price fraction helpers', () => {
  it('parses and formats eighths', () => {
    expect(parsePrice('43 1/2')).toBe(43.5);
    expect(parsePrice('91 3/4')).toBe(91.75);
    expect(parsePrice('38')).toBe(38);
    expect(formatPrice(122.75)).toBe('122 3/4');
    expect(formatPrice(56.875)).toBe('56 7/8');
  });
});
