import type { EngineConfig, Threshold } from './types.js';

/**
 * Numeric comparison epsilon (DD-16): absolute-unit ledgers (book eighths) are
 * exact in IEEE-754; percent-mode multiplications need a relative epsilon.
 * Strictly relative — any absolute floor would break scale invariance for
 * sub-1.0 prices (verified by the property tests).
 */
export function eps(base: number): number {
  return 1e-9 * Math.abs(base);
}

function applyUp(base: number, t: Threshold, tolerance = 0): number {
  const v = t.value - tolerance;
  return t.unit === 'absolute' ? base + v : base * (1 + v / 100);
}

function applyDown(base: number, t: Threshold, tolerance = 0): number {
  const v = t.value - tolerance;
  return t.unit === 'absolute' ? base - v : base * (1 - v / 100);
}

/** Price at/above which a rally of S from `ref` has occurred (§1 "swing of S"). */
export function swingUpTarget(ref: number, cfg: EngineConfig): number {
  return applyUp(ref, cfg.swing, cfg.swingTolerance ?? 0);
}

/** Price at/below which a reaction of S from `ref` has occurred. */
export function swingDownTarget(ref: number, cfg: EngineConfig): number {
  return applyDown(ref, cfg.swing, cfg.swingTolerance ?? 0);
}

/** PP + C — carry-through confirmation above a pivotal point (rules 5a, 10a). */
export function confUpTarget(pp: number, cfg: EngineConfig): number {
  return applyUp(pp, cfg.confirmation);
}

/** PP − C — carry-through confirmation below a pivotal point (rules 5b, 10c). */
export function confDownTarget(pp: number, cfg: EngineConfig): number {
  return applyDown(pp, cfg.confirmation);
}

/** a >= b, epsilon-tolerant. */
export function gte(a: number, b: number): boolean {
  return a >= b - eps(b);
}

/** a <= b, epsilon-tolerant. */
export function lte(a: number, b: number): boolean {
  return a <= b + eps(b);
}

/** a > b, epsilon-tolerant strict. */
export function gt(a: number, b: number): boolean {
  return a > b + eps(b);
}

/** a < b, epsilon-tolerant strict. */
export function lt(a: number, b: number): boolean {
  return a < b - eps(b);
}
