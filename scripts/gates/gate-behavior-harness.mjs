#!/usr/bin/env node
// gate-behavior-harness.mjs — automated PASS/FAIL proof that role-scorer.mjs's
// gates (liveness, timeline, funding_recency) multiply the composite instead
// of voting on it. This is the capstone contribution: Ch.11/16 name the
// "gate-as-vote bug" — a gate that only discounts a score instead of zeroing
// it — as the build failure this harness exists to catch.
//
// It works by constructing synthetic roles with deliberately HIGH votes
// (sponsorship=0.9, fit=0.85) and then closing each gate one at a time,
// asserting the resulting composite is ~0 (below CONFIG.gate_zero). If a
// future change to role-scorer.mjs ever turns a gate back into an additive
// vote, this harness FAILS loudly instead of silently producing a wrong
// recommendation.
//
// Usage: node scripts/gates/gate-behavior-harness.mjs

import { execSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

const GATE_ZERO = 0.05; // must match CONFIG.gate_zero in role-scorer.mjs

// Synthetic test roles: identical high votes, each with exactly one gate closed.
// These are NOT real companies — this harness tests code behavior, not real
// sponsorship data, so fabricated names are appropriate and clearly labeled.
const testRoles = [
  {
    role_id: 'harness-all-gates-open',
    company: 'SYNTHETIC-TEST-CO-A',
    title: '[harness] control case — all gates open',
    sponsorship: { p: 0.9, tier: 'Proven', source: 'record' },
    fit: { p: 0.85, source: 'model-judgment' },
    liveness: { factor: 1.0, source: 'record' },
    timeline: { factor: 1.0, source: 'your-input' },
    funding_recency: { factor: 1.0, source: 'record' },
  },
  {
    role_id: 'harness-liveness-closed',
    company: 'SYNTHETIC-TEST-CO-B',
    title: '[harness] liveness gate closed, all else high',
    sponsorship: { p: 0.9, tier: 'Proven', source: 'record' },
    fit: { p: 0.85, source: 'model-judgment' },
    liveness: { factor: 0.0, source: 'record' },
    timeline: { factor: 1.0, source: 'your-input' },
    funding_recency: { factor: 1.0, source: 'record' },
  },
  {
    role_id: 'harness-timeline-closed',
    company: 'SYNTHETIC-TEST-CO-C',
    title: '[harness] timeline gate closed, all else high',
    sponsorship: { p: 0.9, tier: 'Proven', source: 'record' },
    fit: { p: 0.85, source: 'model-judgment' },
    liveness: { factor: 1.0, source: 'record' },
    timeline: { factor: 0.0, source: 'your-input' },
    funding_recency: { factor: 1.0, source: 'record' },
  },
  {
    role_id: 'harness-funding-closed',
    company: 'SYNTHETIC-TEST-CO-D',
    title: '[harness] funding_recency gate closed, all else high',
    sponsorship: { p: 0.9, tier: 'Proven', source: 'record' },
    fit: { p: 0.85, source: 'model-judgment' },
    liveness: { factor: 1.0, source: 'record' },
    timeline: { factor: 1.0, source: 'your-input' },
    funding_recency: { factor: 0.05, source: 'record' },
  },
];

function main() {
  const outDir = path.join('data', 'examples');
  fs.mkdirSync(outDir, { recursive: true });
  const inputPath = path.join(outDir, 'gate-behavior-harness-input.json');
  fs.writeFileSync(inputPath, JSON.stringify(testRoles, null, 2));

  console.log('=== Gate Behavior Harness ===');
  console.log(`Testing ${testRoles.length} synthetic roles (not real companies) against role-scorer.mjs\n`);

  execSync(
    `node scripts/score/role-scorer.mjs ${inputPath} --out-dir ${outDir} --md ${path.join(outDir, 'gate-behavior-harness-report.md')}`,
    { stdio: 'inherit' }
  );

  const results = JSON.parse(fs.readFileSync(path.join(outDir, 'role-scores.json'), 'utf8')).roles;

  let allPass = true;
  console.log('\n=== PASS/FAIL ===');
  for (const r of results) {
    const isControl = r.role_id === 'harness-all-gates-open';
    let pass;
    if (isControl) {
      // control case: should NOT be gated — composite should reflect the high votes
      pass = r.composite > GATE_ZERO && r.recommendation !== 'Skip';
      console.log(`${pass ? 'PASS' : 'FAIL'}  ${r.role_id}  composite=${r.composite}  rec=${r.recommendation}  (expected: ungated, composite > ${GATE_ZERO})`);
    } else {
      // gated case: composite MUST be at or below gate_zero despite high votes
      pass = r.composite <= GATE_ZERO;
      console.log(`${pass ? 'PASS' : 'FAIL'}  ${r.role_id}  composite=${r.composite}  rec=${r.recommendation}  (expected: gated, composite <= ${GATE_ZERO} despite sponsorship=0.9/fit=0.85)`);
    }
    if (!pass) allPass = false;
  }

  console.log(`\n${allPass ? '✓ ALL GATES BEHAVE AS MULTIPLIERS' : '✗ GATE-AS-VOTE BUG DETECTED — a gate failed to zero the composite'}`);
  process.exit(allPass ? 0 : 1);
}

main();