/**
 * Key Price groups (RULES.md §7): two member ledgers plus a combined
 * Key Price ledger, with optional cross-coupling (DD-13).
 */

import type { Bar, CouplingHints, EngineConfig, EngineEvent, LedgerState } from './types.js';
import { capsFromKeyPriceColumn, initialState, isUp } from './types.js';
import { step } from './engine.js';

export type KeyPriceMethod = 'sum' | 'normalized-index';

export interface GroupConfig {
  member: EngineConfig;
  keyPrice: EngineConfig;
  /** DD-13: sub-threshold member swings count when the KP swing qualifies. */
  coupling: boolean;
  /** §7 / DD-14. 'sum' is the book's construction (absolute mode). */
  method: KeyPriceMethod;
  /** First prices of each member at group creation, for 'normalized-index'. */
  normBase?: { a: number; b: number };
}

export interface GroupState {
  a: LedgerState;
  b: LedgerState;
  kp: LedgerState;
}

export function initialGroupState(): GroupState {
  return { a: initialState(), b: initialState(), kp: initialState() };
}

/** Combine two member bars into the Key Price bar (DD-12, DD-14). */
export function keyPriceBar(a: Bar, b: Bar, cfg: GroupConfig): Bar {
  const scaleA = cfg.method === 'normalized-index' && cfg.normBase ? 100 / cfg.normBase.a : 1;
  const scaleB = cfg.method === 'normalized-index' && cfg.normBase ? 100 / cfg.normBase.b : 1;
  return {
    date: a.date,
    open: a.open * scaleA + b.open * scaleB,
    high: a.high * scaleA + b.high * scaleB,
    low: a.low * scaleA + b.low * scaleB,
    close: a.close * scaleA + b.close * scaleB,
  };
}

export interface GroupStepResult {
  state: GroupState;
  events: { a: EngineEvent[]; b: EngineEvent[]; kp: EngineEvent[] };
}

function couplingFrom(kpEvents: EngineEvent[], kpActive: import('./types.js').Column | null): CouplingHints {
  let up = false;
  let down = false;
  for (const e of kpEvents) {
    if (e.type === 'RECORD') {
      if (isUp(e.column)) up = true;
      else down = true;
    }
  }
  // §12 confirmation caps derive from the Key Price's *current* column (its
  // commitment level), which persists across days it does not record.
  const caps = capsFromKeyPriceColumn(kpActive);
  return { kpRecordedUp: up, kpRecordedDown: down, kpUpCap: caps.up, kpDownCap: caps.down };
}

/**
 * Step a whole group for one day. The KP ledger is evaluated first (it is
 * self-contained), then the members with coupling hints derived from the KP
 * ledger's recordings (DD-13).
 */
export function stepGroup(state: GroupState, bars: { a: Bar; b: Bar }, cfg: GroupConfig): GroupStepResult {
  if (bars.a.date !== bars.b.date) {
    throw new Error(`group bars must share a date: ${bars.a.date} vs ${bars.b.date}`);
  }
  const kpBar = keyPriceBar(bars.a, bars.b, cfg);
  const kpRes = step(state.kp, kpBar, cfg.keyPrice);
  const hints = cfg.coupling ? couplingFrom(kpRes.events, kpRes.state.active) : undefined;
  const aRes = step(state.a, bars.a, cfg.member, hints);
  const bRes = step(state.b, bars.b, cfg.member, hints);
  return {
    state: { a: aRes.state, b: bRes.state, kp: kpRes.state },
    events: { a: aRes.events, b: bRes.events, kp: kpRes.events },
  };
}
