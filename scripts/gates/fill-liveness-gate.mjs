#!/usr/bin/env node
// fill-liveness-gate.mjs — feeds REAL Playwright liveness checks into a
// roles.json file so role-scorer.mjs's liveness gate reflects verified
// reality, not a hand-typed default.
//
// Why this exists (TA feedback + capstone Ch.11/16 gate-behavior requirement):
// role-scorer.mjs already treats `liveness.factor` as a multiplying GATE —
// but nothing in this repo ever WROTE a real liveness.factor. Every roles.json
// in the wild has `liveness: { factor: 1.0, source: "record" }` hand-typed.
// This script closes that gap: it actually visits each role's job URL with
// Playwright, classifies it, and writes the REAL result back.
//
// Usage:
//   node scripts/gates/fill-liveness-gate.mjs <roles-with-urls.json> [--out out.json]
//
// Input file must have a `job_url` field per role (in addition to the fields
// role-scorer.mjs expects). Roles without a job_url are left untouched and
// flagged in the console output — never silently guessed.

import fs from 'node:fs';
import path from 'node:path';
import { chromium } from 'playwright';
import { checkUrlLiveness } from '../ats/liveness-browser.mjs';

const RESULT_TO_FACTOR = { active: 1.0, expired: 0.0, uncertain: 0.5 };

async function main() {
  const args = process.argv.slice(2);
  const src = args.find((a) => !a.startsWith('--'));
  if (!src || !fs.existsSync(src)) {
    console.error('Usage: node scripts/gates/fill-liveness-gate.mjs <roles-with-urls.json> [--out out.json]');
    process.exit(2);
  }
  const oi = args.indexOf('--out');
  const outPath = oi >= 0 ? args[oi + 1] : src.replace(/\.json$/, '.liveness-filled.json');

  const roles = JSON.parse(fs.readFileSync(src, 'utf8'));
  const list = Array.isArray(roles) ? roles : roles.roles || [];

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  let checked = 0, skipped = 0;
  for (const role of list) {
    if (!role.job_url) {
      console.log(`⚠ ${role.role_id ?? role.company}: no job_url — leaving liveness untouched`);
      skipped++;
      continue;
    }
    const { result, reason } = await checkUrlLiveness(page, role.job_url);
    const factor = RESULT_TO_FACTOR[result] ?? 0.5;
    role.liveness = {
      factor,
      source: 'record',       // now genuinely produced by a script run, not hand-typed
      checked_url: role.job_url,
      checked_result: result,
      checked_reason: reason,
      checked_at: new Date().toISOString(),
    };
    const icon = result === 'active' ? '✅' : result === 'expired' ? '❌' : '⚠️';
    console.log(`${icon} ${result.padEnd(10)} factor=${factor}  ${role.role_id ?? role.company}`);
    checked++;
  }

  await browser.close();

  fs.writeFileSync(outPath, JSON.stringify(list, null, 2));
  console.log(`\n✓ checked ${checked} role(s), skipped ${skipped} (no job_url)`);
  console.log(`  wrote ${path.relative(process.cwd(), outPath)}`);
}

main().catch((err) => {
  console.error('Fatal:', err.message);
  process.exit(1);
});