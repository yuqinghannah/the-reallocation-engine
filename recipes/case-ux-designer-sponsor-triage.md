---
status: RUNNABLE-LIVE
todos_open: 1
last_gate: funding_recency
attestation: assignments/submissions/yuqinghannah/worked-run.md
recipe_version: 0.3.0
---

# ux-designer-sponsor-triage

## Purpose
For an F-1 UX/Product Designer on STEM OPT, evaluate and prioritize open
Product Designer / UX Designer postings by (1) whether the hiring company has
a *documented history of sponsoring designer-titled H-1B roles specifically*
(not just any H-1B), (2) how recent its last funding round was, and (3)
whether the specific posting is still live — before spending application
time on it.

Use this mode when: you have a shortlist of open Product/UX Designer roles
and need to rank them by sponsorship probability before applying. Do not use
this mode after you already have an offer — sponsorship-history data
describes company patterns, not guarantees for a specific hire.

## Source Inventory
- `data/80-days-to-stay/data/SEC_DOL_H1b_data_mapped.csv` — company-level
  SEC Form D funding data joined with DOL H-1B petition history. Confirmed
  columns (read directly from the file header): `company_name, industry,
  website, city, state, zip_code, phone, year_incorporated,
  company_age_years, executive_officers, board_directors, total_funding,
  latest_funding_amount, latest_funding_stage, latest_funding_date,
  Total Approvals, Total Denials, Approval_Rate, median_salary_offered,
  top_job_titles_sponsored`
- `top_job_titles_sponsored` is the field this mode filters on — it is a
  literal list of job titles the company has sponsored H-1Bs for in the past
  (e.g. `['Senior UX Designer']`, `['Product Designer']`). This means design
  roles can be matched directly by title text, without needing a separate
  SOC-code mapping step.
- `npm run ats:liveness -- <job-url>` — posting liveness check (GATE),
  called by `scripts/gates/fill-liveness-gate.mjs` (below).
- **`scripts/gates/fill-liveness-gate.mjs`** — NEW this revision. Runs
  Playwright liveness checks against real job URLs and writes a real
  `liveness.factor` (1.0 active / 0.0 expired / 0.5 uncertain) back onto each
  role, replacing the hand-typed `factor: 1.0` every prior roles.json in this
  repo carried. `node scripts/gates/fill-liveness-gate.mjs <roles.json>
  [--out out.json]`.
- **`scripts/gates/fill-funding-recency-gate.mjs`** — NEW this revision.
  Looks up each role's company in `SEC_DOL_H1b_data_mapped.csv` and computes
  a real `funding_recency.factor` from `latest_funding_date` (thresholds
  below are [VERIFY] — an authorial judgment call, not a number pinned
  anywhere in the book or repo docs). `node
  scripts/gates/fill-funding-recency-gate.mjs <roles.json> <sec-csv> [--out
  out.json]`.
- `scripts/score/role-scorer.mjs` — now reads `funding_recency.factor` as a
  third gate multiplier (previously only liveness and timeline gated the
  composite).

## Proposed Additions (typed, not yet built)
- [TODO: DATA] Design-specific SOC code cross-reference — the underlying
  DOL data likely carries SOC codes internally, but they are not exposed as
  a column in `SEC_DOL_H1b_data_mapped.csv`. Without them, this mode can only
  match on the *literal job title string* a company used before, not on the
  broader occupational category. Justification: a company that sponsored a
  "Senior Interaction Designer" won't be caught by a search for "UX
  Designer" — title-string matching under-counts real matches.

## Phase Gates
1. **Liveness gate** — now REAL: `scripts/gates/fill-liveness-gate.mjs`
   actually visits each job URL with Playwright and writes back active
   (factor=1.0) / expired (factor=0.0) / uncertain (factor=0.5). Tested
   against 3 real job postings (see Worked Run) — one (Hagerty) turned out
   to be genuinely expired despite my prior assumption it was still live;
   one I assumed was expired ("posted ~1 month ago") turned out active. A
   dead posting zeroes the composite regardless of every other score,
   verified directly (composite = 0.000, see arithmetic trace).
2. **Title-match gate** — the company's `top_job_titles_sponsored` field
   must contain a design-adjacent string. Zero title matches doesn't mean
   "will never sponsor a designer," but it moves the company out of the
   top-confidence tier.
3. **Funding recency gate** — now REAL: `scripts/gates/fill-funding-recency-gate.mjs`
   reads `latest_funding_date` and applies a fixed threshold ([VERIFY] —
   not an established standard): ≤18mo → factor 1.0 (fresh); 18–30mo →
   factor 0.5 (aging); >30mo → factor 0.05 (stale, gate closes); missing or
   company not in the SEC dataset → factor 0.5 ("unknown," never guessed as
   fresh or stale). Tested against a company with a 117-month-old funding
   record (factor=0.05) whose sponsorship/fit votes were deliberately set
   high (0.9/0.85) — the composite still dropped to 0.024, confirming the
   gate closes the door regardless of vote strength.

## What This Mode Can and Cannot Verify
**Can verify:** whether a company's H-1B filing history includes a
design-adjacent job title string, verbatim, from `top_job_titles_sponsored`;
the company's most recent funding stage and date; whether a specific job
posting URL is currently live, expired, or uncertain (via a real Playwright
visit, not an assumption).

**Cannot verify:** whether the company will sponsor *this specific* design
opening (past sponsorship of one title ≠ future sponsorship of a similarly
named but different role); whether a job title that doesn't literally match
a design-adjacent string ("Interaction Designer," "Design Technologist,"
"Experience Designer") was in fact a design role — title-string matching has
no synonym handling; whether a live posting is actually still accepting
applications versus merely not yet taken down; the funding-recency thresholds
(≤18/18–30/>30 months) are an authorial judgment call, not an industry
standard, and may not reflect the actual runway of any specific company;
companies not present in the SEC Form D dataset (confirmed during testing:
none of Hagerty, Nerdio, or Clutch — all real, currently-hiring companies —
appear in this ~6,000-row dataset) get an "unknown" funding-recency factor,
which this mode treats as neutral (0.5), not as evidence of either freshness
or staleness.

## Output Contract
- Agent log: `logs/ux-designer-sponsor-triage-run.json` — one record per
  company checked: `company_name`, `matched_title_strings`,
  `latest_funding_stage`, `latest_funding_date`, `approval_rate`,
  `liveness_result`, `funding_recency_factor`.
- Human report: Markdown table — one row per company, tier (Top / Watch /
  Drop) with a one-line reason.
- These are never the same file (P5).

## Stop Conditions
- If `top_job_titles_sponsored` is empty or unparseable for a company, the
  mode reports "no title data," never assumes zero history means "won't
  sponsor."
- If `ats:liveness` cannot reach a URL (network error vs. dead posting), the
  mode reports "uncertain" (factor=0.5), never guesses active or expired.
- If a company is not found in the SEC/DOL dataset, funding recency is
  reported "unknown" (factor=0.5), never assumed fresh or stale.

## RUN_LOG Template
```
### <date>
- Mode: ux-designer-sponsor-triage vX.X
- Inputs: <N companies/roles checked, source>
- Commands run: <verbatim>
- Result: <N top-tier, N watch, N dropped>
- Open issues: <e.g. title-matching still manual, no SOC cross-reference>
```