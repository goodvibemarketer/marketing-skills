/**
 * Price fraction helpers. The 1938–40 charts quote prices in eighths;
 * fixture files store them as strings like "43 1/2" (exact in IEEE-754).
 */

const EIGHTHS: Record<string, number> = {
  '1/8': 0.125,
  '1/4': 0.25,
  '3/8': 0.375,
  '1/2': 0.5,
  '5/8': 0.625,
  '3/4': 0.75,
  '7/8': 0.875,
};

export function parsePrice(text: string): number {
  const t = text.trim().replace(/\s+/g, ' ');
  const m = t.match(/^(\d+)(?: (\d\/\d))?$/);
  if (!m) throw new Error(`unparseable price: "${text}"`);
  const whole = Number(m[1]);
  const frac = m[2] ? EIGHTHS[m[2]] : 0;
  if (m[2] && frac === undefined) throw new Error(`unparseable fraction: "${text}"`);
  return whole + (frac ?? 0);
}

export function formatPrice(value: number): string {
  const whole = Math.floor(value);
  const rem = value - whole;
  for (const [txt, v] of Object.entries(EIGHTHS)) {
    if (Math.abs(rem - v) < 1e-9) return `${whole} ${txt}`;
  }
  if (Math.abs(rem) < 1e-9) return String(whole);
  return String(value);
}
