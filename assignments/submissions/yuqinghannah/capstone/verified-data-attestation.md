# Verified-Data Attestation — gate-behavior-harness

## 1. Verified-vs-Inferred Boundary Table

Every field this contribution emits or consumes, labeled by source type
(record / script-output / model-inference / your-input / missing):

| Field | Source Type | Where It Comes From |
|---|---|---|
| `sponsorship.p` (test roles) | your-input | Hardcoded in gate-behavior-harness.mjs as a deliberately high synthetic value (0.9) to isolate gate behavior — explicitly labeled SYNTHETIC-TEST-CO-*, never presented as a real company |
| `fit.p` (test roles) | your-input | Same as above (0.85), synthetic |
| `liveness.factor` (real Mode Build data) | script-output | Produced by scripts/gates/fill-liveness-gate.mjs, which calls Playwright via checkUrlLiveness against a real, live URL — this is a script measurement, not a guess |
| `funding_recency.factor` (real Mode Build data) | script-output | Produced by scripts/gates/fill-funding-recency-gate.mjs, computed from the record field latest_funding_date in SEC_DOL_H1b_data_mapped.csv, using a fixed threshold rule |
| `latest_funding_date` (source data) | record | Read directly from SEC_DOL_H1b_data_mapped.csv, a real SEC Form D + DOL H-1B joined dataset already in this repo |
| Funding-recency thresholds (18mo/30mo) | model-inference / your-input | My own judgment call — explicitly marked [VERIFY] in the code comments. Not pinned by the book or any repo doc. Not validated against a larger sample. |
| `composite` (per role) | script-output | Computed by role-scorer.mjs's existing arithmetic (vote_sum × gate_product) — every component of this arithmetic is itself traced in the JSON output |
| PASS/FAIL verdict (harness) | script-output | Computed by a hardcoded threshold comparison (composite <= 0.05) in gate-behavior-harness.mjs — deterministic, not a judgment call |
| "gate-as-vote bug not detected" (this run) | script-output | Directly read from the harness's own exit code and printed summary line — not a claim I am asserting independently of the tool |

## 2. Every Number Traces

| Number Reported | Script | Record / Basis |
|---|---|---|
| 4 synthetic roles tested | `gate-behavior-harness.mjs` | Hardcoded array in the script itself (visible in source, not hidden) |
| composite=0.57 (control case) | `role-scorer.mjs` via harness | Arithmetic: (0.9·0.35 + 0.85·0.3) × 1 × 1 × 1 — every term shown in `role-scores.json`'s `trace` field |
| composite=0 (liveness closed) | `role-scorer.mjs` via harness | Arithmetic: same vote_sum × 0 (liveness) × 1 × 1 = 0 |
| composite=0 (timeline closed) | `role-scorer.mjs` via harness | Arithmetic: same vote_sum × 1 × 0 (timeline) × 1 = 0 |
| composite=0.0285 (funding closed) | `role-scorer.mjs` via harness | Arithmetic: same vote_sum × 1 × 1 × 0.05 (funding_recency) = 0.0285 |
| 4/4 PASS | `gate-behavior-harness.mjs` stdout | Printed directly by the harness's own assertion logic, pasted verbatim in the Worked Run — not summarized or rounded by me |

If a number in this contribution cannot be traced this way, it does not
appear in this attestation or in the Worked Run — per the zero-condition
rule, an untraceable number is worse than an admitted gap.

## 3. Ethics Gate — Passing

### (a) Privacy
Command run (on `contrib/yuqinghannah-gate-behavior-harness` branch, the
branch this contribution ships on):

```
npm run doctor
```

Relevant real output:
```
PRIVACY (no personal data committed)
  [check] no private/PII paths are tracked
```

**Verified:** this contribution touches no files under `data/ats/` or
`private/` — it only reads `SEC_DOL_H1b_data_mapped.csv` (public,
already-tracked company-level data) and writes synthetic, clearly-labeled
test fixtures. No real company's sponsorship or funding data is used in
the harness itself (only in the separate, already-submitted Mode Build
work, which uses real company names transparently, not personal data).

**Honest gap found in the same doctor run (not hidden):** doctor also
reports our new recipe `case-gate-behavior-harness.md` under "missing
frontmatter" (45 total), even though the file demonstrably *does* carry
full frontmatter (`status`, `todos_open`, `last_gate`, `attestation`,
`recipe_version` — visible in the file itself). This is either a blind
spot in doctor.mjs's detection logic, or a format mismatch I have not
root-caused. I am flagging it rather than silently omitting it, since
this attestation's whole point is "don't hide a number/finding that
doesn't fit the story."

### (b) Honesty
- No metric in this contribution is invented. The 4/4 PASS result is the
  harness's own deterministic output, not a summary I wrote by hand.
- The funding-recency thresholds are explicitly labeled a judgment call
  (`[VERIFY]`), not presented as an established standard — this is the
  single largest "honesty" risk in this contribution, and it is disclosed
  in three separate places: the gate script's code comments, the AI
  recipe's Required Reads section, and this attestation.
- Nothing in this contribution's output "looks done" without a script
  behind it — the harness's PASS/FAIL table is generated by executing
  real code against `role-scorer.mjs`, not asserted as a finding with no
  script.

**Gate result: PASSING.** Both privacy and honesty checks succeed; the
one honest gap found (the frontmatter-detection discrepancy) does not
block the gate — it is disclosed, not concealed, and does not involve
private data or a fabricated metric.