/**
 * Property tests (Phase 3 item 4): in percent mode, the same *relative* price
 * path must produce the identical column/event sequence at any absolute price
 * level (DD-15, DD-16). Uses a deterministic seeded PRNG — no dependencies.
 */
import { describe, expect, it } from 'vitest';
import { type Bar, type EngineConfig, initialState, step } from '../src/index.js';

const PCT: EngineConfig = {
  swing: { value: 6, unit: 'percent' },
  confirmation: { value: 3, unit: 'percent' },
};

/** Deterministic LCG (Numerical Recipes constants). */
function lcg(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (Math.imul(1664525, s) + 1013904223) >>> 0;
    return s / 2 ** 32;
  };
}

/** Random-walk daily bars as *relative* multipliers of a base price. */
function randomWalk(seed: number, days: number, base: number): Bar[] {
  const rnd = lcg(seed);
  const bars: Bar[] = [];
  let level = 1;
  for (let i = 0; i < days; i++) {
    const drift = (rnd() - 0.5) * 0.06; // ±3% daily drift
    const range = rnd() * 0.05; // up to 5% intraday range
    level = Math.max(0.05, level * (1 + drift));
    const high = level * (1 + range / 2);
    const low = level * (1 - range / 2);
    const date = `2020-${String(1 + Math.floor(i / 28)).padStart(2, '0')}-${String(1 + (i % 28)).padStart(2, '0')}`;
    bars.push({ date, open: level * base, high: high * base, low: low * base, close: level * base });
  }
  return bars;
}

function columnSequence(bars: Bar[], cfg: EngineConfig): string[] {
  let state = initialState();
  const seq: string[] = [];
  for (const bar of bars) {
    const r = step(state, bar, cfg);
    state = r.state;
    for (const e of r.events) {
      if (e.type === 'RECORD') seq.push(`${bar.date}:${e.column}:${e.rule}`);
      if (e.type === 'UNDERLINE') seq.push(`${bar.date}:UL:${e.column}:${e.color}`);
      if (e.type === 'SIGNAL') seq.push(`${bar.date}:${e.kind}`);
    }
  }
  return seq;
}

describe('percent mode is scale-invariant (DD-15/DD-16)', () => {
  const SCALES = [1, 8, 1024, 1000, 0.001, 63417.5]; // powers of two are float-exact; others exercise the epsilon
  for (let seed = 1; seed <= 25; seed++) {
    it(`seed ${seed}: identical event sequences across price scales`, () => {
      const reference = columnSequence(randomWalk(seed, 400, 1), PCT);
      expect(reference.length).toBeGreaterThan(0); // the walk must actually exercise the machine
      for (const scale of SCALES) {
        const scaled = columnSequence(randomWalk(seed, 400, scale), PCT);
        expect(scaled).toEqual(reference);
      }
    });
  }

  it('absolute mode is translation-sensitive but percent mode is not (sanity contrast)', () => {
    const ABS: EngineConfig = { swing: { value: 6, unit: 'absolute' }, confirmation: { value: 3, unit: 'absolute' } };
    const small = columnSequence(randomWalk(7, 400, 10), ABS); // 6 points on a $10 stock ≈ nothing fires
    const large = columnSequence(randomWalk(7, 400, 1000), ABS);
    expect(small).not.toEqual(large);
  });
});
