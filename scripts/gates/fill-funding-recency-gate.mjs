#!/usr/bin/env node
// fill-funding-recency-gate.mjs — looks up each role's company in the real
// SEC/DOL dataset and computes a REAL funding-recency gate factor from
// latest_funding_date, instead of the "currently eyeballed manually, not
// scripted" placeholder the recipe honestly flagged.
//
// THRESHOLDS ARE [VERIFY] — an authorial judgment call, not a number pinned
// anywhere in the book or the repo's docs. They are logged as such below so
// nobody mistakes this for an established industry standard.
//
//   <= 18 months since latest_funding_date  -> factor 1.0 (fresh)
//   18-30 months                            -> factor 0.5 (aging, not gated)
//   > 30 months                             -> factor 0.05 (stale -> gated closed)
//   missing / company not found in CSV      -> factor 0.5, flagged "unknown"
//
// Usage:
//   node scripts/gates/fill-funding-recency-gate.mjs <roles.json> data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv [--out out.json]

import fs from 'node:fs';
import path from 'node:path';

const FRESH_MONTHS = 18;
const STALE_MONTHS = 30;

function monthsSince(dateStr, now = new Date()) {
  const d = new Date(dateStr);
  if (isNaN(d.getTime())) return null;
  return (now.getFullYear() - d.getFullYear()) * 12 + (now.getMonth() - d.getMonth());
}

function fundingFactor(dateStr) {
  if (!dateStr) return { factor: 0.5, note: 'no latest_funding_date on record — treated as unknown, not fresh or stale' };
  const months = monthsSince(dateStr);
  if (months == null) return { factor: 0.5, note: `unparseable date "${dateStr}" — treated as unknown` };
  if (months <= FRESH_MONTHS) return { factor: 1.0, note: `${months}mo old — fresh (<= ${FRESH_MONTHS}mo threshold)` };
  if (months <= STALE_MONTHS) return { factor: 0.5, note: `${months}mo old — aging (${FRESH_MONTHS}-${STALE_MONTHS}mo band)` };
  return { factor: 0.05, note: `${months}mo old — stale (> ${STALE_MONTHS}mo threshold) — gate closes` };
}

// CSV parser that correctly handles quoted fields containing embedded commas
// (e.g. executive_officers: "Brandon Brunet, Edward Livingston, ...").
// The naive split(',') version silently misaligned every column after the
// first quoted comma — a real bug found while running this on real data
// (see WORKED_RUN break-attempt notes).
function parseCsvLine(line) {
  const cells = [];
  let cur = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (inQuotes) {
      if (ch === '"' && line[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') { inQuotes = false; }
      else { cur += ch; }
    } else {
      if (ch === '"') inQuotes = true;
      else if (ch === ',') { cells.push(cur); cur = ''; }
      else { cur += ch; }
    }
  }
  cells.push(cur);
  return cells;
}

function parseCsv(text) {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = parseCsvLine(headerLine);
  return lines.map((line) => {
    const cells = parseCsvLine(line);
    const row = {};
    headers.forEach((h, i) => { row[h] = cells[i] ?? ''; });
    return row;
  });
}

async function main() {
  const args = process.argv.slice(2);
  const rolesPath = args[0];
  const csvPath = args[1];
  if (!rolesPath || !csvPath || !fs.existsSync(rolesPath) || !fs.existsSync(csvPath)) {
    console.error('Usage: node scripts/gates/fill-funding-recency-gate.mjs <roles.json> <sec-csv> [--out out.json]');
    process.exit(2);
  }
  const oi = args.indexOf('--out');
  const outPath = oi >= 0 ? args[oi + 1] : rolesPath.replace(/\.json$/, '.funding-filled.json');

  const roles = JSON.parse(fs.readFileSync(rolesPath, 'utf8'));
  const list = Array.isArray(roles) ? roles : roles.roles || [];
  const csvRows = parseCsv(fs.readFileSync(csvPath, 'utf8'));
  const byName = new Map(csvRows.map((r) => [r.company_name?.trim().toLowerCase(), r]));

  for (const role of list) {
    const match = byName.get((role.company || '').trim().toLowerCase());
    if (!match) {
      role.funding_recency = { factor: 0.5, source: 'record', note: 'company not found in SEC/DOL dataset — treated as unknown, not fresh or stale', checked_at: new Date().toISOString() };
      console.log(`⚠ ${role.role_id ?? role.company}: not in SEC dataset — factor=0.5 (unknown)`);
      continue;
    }
    const { factor, note } = fundingFactor(match.latest_funding_date);
    role.funding_recency = {
      factor,
      source: 'record',
      latest_funding_date: match.latest_funding_date || null,
      latest_funding_stage: match.latest_funding_stage || null,
      note,
      checked_at: new Date().toISOString(),
    };
    const icon = factor >= 1.0 ? '✅' : factor >= 0.3 ? '⚠️' : '❌';
    console.log(`${icon} factor=${factor}  ${role.role_id ?? role.company}  (${note})`);
  }

  fs.writeFileSync(outPath, JSON.stringify(list, null, 2));
  console.log(`\n✓ wrote ${path.relative(process.cwd(), outPath)}`);
}

main().catch((err) => { console.error('Fatal:', err.message); process.exit(1); });