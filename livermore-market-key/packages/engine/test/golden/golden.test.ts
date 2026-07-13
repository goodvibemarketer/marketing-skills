/**
 * Golden-master acceptance suite (Phase 3 items 1–2): the book's own Charts
 * One–Sixteen replayed through the engine in fixed-point mode (6/3/12).
 *
 * The suite asserts the engine reproduces the book's column placements and
 * fails on any divergence not explicitly catalogued (with a reason) in a
 * fixture's `knownDivergences`. It is skipped only when no fixtures are present
 * (so the repo builds before transcription lands); once fixtures exist the
 * assertions are hard.
 */
import { existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { formatMismatches, loadFixtures, replayCharts } from './harness.js';

const here = dirname(fileURLToPath(import.meta.url));
const fixturesDir = join(here, '..', 'fixtures');

const hasFixtures =
  existsSync(fixturesDir) && readdirSync(fixturesDir).some((f) => /^chart-\d+\.json$/.test(f));

describe.skipIf(!hasFixtures)('golden master — book Charts One–Sixteen (fixed-point 6/3/12)', () => {
  it('reproduces the book column placements with no unexplained divergences', () => {
    const fixtures = loadFixtures(fixturesDir);
    expect(fixtures.length).toBeGreaterThan(0);
    const report = replayCharts(fixtures);

    if (report.unexplained.length > 0) {
      throw new Error(
        `${report.unexplained.length} unexplained divergence(s) from the book ` +
          `(${report.matchedEntries}/${report.totalEntries} entries matched):\n` +
          formatMismatches(report.unexplained),
      );
    }
    expect(report.unexplained).toHaveLength(0);
  });

  it('matches a high fraction of the book entries exactly (engine faithfulness)', () => {
    const fixtures = loadFixtures(fixturesDir);
    const report = replayCharts(fixtures);
    // The book is a hand ledger; a few catalogued divergences are expected,
    // but the overwhelming majority of column placements must match.
    const ratio = report.matchedEntries / Math.max(1, report.totalEntries);
    expect(ratio).toBeGreaterThan(0.9);
  });
});

describe.skipIf(hasFixtures)('golden master — awaiting fixtures', () => {
  it('placeholder until chart fixtures are transcribed', () => {
    expect(hasFixtures).toBe(false);
  });
});
