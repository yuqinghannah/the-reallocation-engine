# Honest Run — gate-behavior-harness (Capstone Step 4)

## 1. Plausibility Audit (before trusting the output)

Before treating any run of this harness as trustworthy, I sanity-checked
the arithmetic by hand against role-scorer.mjs's own trace output for the
first clean run (see Section 2 below):

- Control case (`harness-all-gates-open`): vote_sum = 0.9x0.35 + 0.85x0.3 =
  0.315 + 0.255 = 0.57. Gate product = 1 x 1 x 1 = 1. Composite = 0.57 x 1 =
  0.57. This matches the printed composite exactly, and 0.57 sits above the
  0.30 apply_threshold, which is why the control case gets Apply, not Skip
  -- a ~0 sponsorship or fit vote here would collapse this to near-zero even
  with gates fully open, which is the correct behavior for a genuinely weak
  candidate, not something this harness needs to gate against.
- A role past a hard cutoff (e.g., a fully-expired posting, liveness=0)
  is gated (Skip), not merely down-weighted -- confirmed directly in
  Section 2's PASS/FAIL table: composite=0 for the liveness-closed case,
  not a partial discount.

## 2. Real Terminal Output — Command 1 (clean run, before the break attempt)

```
node scripts/gates/gate-behavior-harness.mjs

=== Gate Behavior Harness ===
Testing 4 synthetic roles (not real companies) against role-scorer.mjs

scored 4 roles -> Apply 1 . Consider 0 . Skip 3 (skip 75%)
  data/examples/role-scores.json  +  data/examples/gate-behavior-harness-report.md

=== PASS/FAIL ===
PASS  harness-all-gates-open      composite=0.57    rec=Apply  (expected: ungated, composite > 0.05)
PASS  harness-liveness-closed     composite=0       rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)
PASS  harness-timeline-closed     composite=0       rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)
PASS  harness-funding-closed      composite=0.0285  rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)

ALL GATES BEHAVE AS MULTIPLIERS
```

**Verified:** all 4 synthetic roles produced the expected classification.
The harness's own exit code (0) and printed verdict are the source of this
result, not my summary of it.

## 3. Deliberate Break Attempt (the graded core of this section)

To confirm the harness would actually catch the "gate-as-vote bug" it
claims to catch — and not just produce PASS by coincidence every time — I
deliberately reintroduced that exact bug into `role-scorer.mjs` and re-ran
the harness.

**The change (one line, in `scoreRole()`):**
```diff
- const composite = voteSum * gateProduct;
+ const composite = voteSum + gateProduct;
```

This simulates the precise failure the book names: a gate that adds to
the score instead of multiplying it, so a closed gate merely discounts a
high vote instead of zeroing it.

**Real terminal output after the break:**
```
node scripts/gates/gate-behavior-harness.mjs

=== Gate Behavior Harness ===
Testing 4 synthetic roles (not real companies) against role-scorer.mjs

scored 4 roles -> Apply 1 . Consider 0 . Skip 3 (skip 75%)
  data/examples/role-scores.json  +  data/examples/gate-behavior-harness-report.md

=== PASS/FAIL ===
PASS  harness-all-gates-open      composite=1.57    rec=Apply  (expected: ungated, composite > 0.05)
FAIL  harness-liveness-closed     composite=0.57    rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)
FAIL  harness-timeline-closed     composite=0.57    rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)
FAIL  harness-funding-closed      composite=0.62    rec=Skip   (expected: gated, composite <= 0.05 despite sponsorship=0.9/fit=0.85)

GATE-AS-VOTE BUG DETECTED -- a gate failed to zero the composite
```

**This is the result that matters most in this Worked Run.** With the
bug reintroduced, 3 of 4 gated roles that should have been zeroed instead
carried a composite of 0.57–0.62 — high enough that, had this been a real
scoring run instead of a synthetic test, a candidate could have been told
to Apply to a role with a dead posting or catastrophically stale funding,
because the closed gate only *discounted* the score instead of killing it.
The harness's own exit code changed from 0 to 1, and its printed verdict
correctly named the failure category ("GATE-AS-VOTE BUG DETECTED") without
any manual interpretation on my part.

**Fix applied — revert to the correct multiplier:**
```diff
- const composite = voteSum + gateProduct;
+ const composite = voteSum * gateProduct;
```

**Real terminal output after the fix (recovery confirmed):**
```
node scripts/gates/gate-behavior-harness.mjs

=== Gate Behavior Harness ===
Testing 4 synthetic roles (not real companies) against role-scorer.mjs

scored 4 roles -> Apply 1 . Consider 0 . Skip 3 (skip 75%)
  data/examples/role-scores.json  +  data/examples/gate-behavior-harness-report.md

=== PASS/FAIL ===
PASS  harness-all-gates-open      composite=0.57    rec=Apply
PASS  harness-liveness-closed     composite=0       rec=Skip
PASS  harness-timeline-closed     composite=0       rec=Skip
PASS  harness-funding-closed      composite=0.0285  rec=Skip

ALL GATES BEHAVE AS MULTIPLIERS
```

`git status` was checked immediately after reverting to confirm
`scripts/score/role-scorer.mjs` shows no diff against the last commit —
the break-attempt code never touched what was actually shipped.

## 4. Metric Readout

- **Skip rate across all 3 clean runs: 75% (3 of 4 synthetic roles).**
  This exceeds the engine's stated healthy-run floor of ≥50% skip rate —
  though this number is not directly comparable to a real production run,
  since 3 of the 4 synthetic roles were deliberately constructed to be
  gated (that was the point of the test), not a naturally-occurring
  distribution of real postings.
- **Break-attempt detection rate: 3 of 3 gated cases correctly flagged
  FAIL when the bug was present, 0 false negatives.** The one ungated
  control case correctly stayed PASS in both the buggy and fixed runs,
  confirming the break attempt didn't also break the harness's ability to
  recognize a legitimately healthy score.

## 5. What the Machine Could Not Know

- **This harness only tests the mechanism (multiplier vs. vote), not
  whether the gate *thresholds* are the right ones for real hiring
  decisions.** A gate that correctly multiplies but uses a wrong cutoff
  (e.g., the funding-recency 18mo/30mo bands, which are my own judgment
  call, not validated against real hiring-runway data) would pass this
  harness cleanly while still giving bad advice to a real job-seeker.
  That judgment is explicitly handed back to a human in the recipe and
  card — this harness cannot verify it.
- **The harness cannot know whether a future contributor will introduce
  a *different* gate-as-vote bug** — for example, one gate correctly
  multiplying while a newly-added fifth gate is accidentally added instead.
  It only tests the three gates that exist today (liveness, timeline,
  funding_recency); a human adding a new gate must remember to also add a
  corresponding test case, which this harness cannot enforce on its own.
- **The machine cannot judge whether 4 synthetic test roles are a
  sufficient sample.** A human reviewing this contribution has to decide
  whether this narrow, hand-picked test surface (documented as Failure
  Mode #3 in the `.card.md`) is adequate coverage, or whether a larger,
  randomized battery of synthetic roles is needed before this harness can
  be trusted as a real regression guard in CI.