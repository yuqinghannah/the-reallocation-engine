# gate-behavior-harness -- Human Card

## Purpose
This is the plain-language companion to case-gate-behavior-harness.md
(the AI recipe). It answers: what does this tool actually do, what can a
human trust it to verify, and where does it fall short -- written for
someone deciding whether to merge this, not for an agent executing it.

In one sentence: this tool proves that role-scorer.mjs's phase gates
(liveness, timeline, funding recency) genuinely zero out a role's score
when closed, instead of just quietly discounting it -- which is the
exact bug this book names as the capstone's representative build failure
(the "gate-as-vote bug").

## What It Can Verify
- Whether closing any one of the three gates (liveness, timeline,
  funding_recency) reduces a high-scoring synthetic role's composite to
  at or below the configured gate-zero threshold (0.05), regardless of
  how high the sponsorship and fit votes are.
- Whether the "control" case (all gates open) is correctly left ungated --
  proving the test isolates each gate's individual effect rather than
  just checking that everything trends toward zero.
- Whether role-scorer.mjs crashes when fed a role missing an expected
  field -- because the harness doesn't catch its own exceptions, a crash
  in the scorer surfaces as a harness failure, not a false pass.

## What It Cannot Verify
- Whether the gate thresholds themselves are correct for real hiring
  decisions -- this harness only checks that the mechanism (multiplier
  vs. additive vote) works as designed. It does not validate that 0.05 is
  the right cutoff, or that a 0.5 factor for an "aging" funding round is
  the right business judgment. Those are separate, unvalidated
  authorial choices (flagged [VERIFY] in the gate scripts themselves).
- Whether real-world roles will ever actually produce the exact synthetic
  conditions tested here (sponsorship=0.9, fit=0.85, one gate fully
  closed). Real data is messier -- partial gate closures, missing fields,
  multiple gates degraded simultaneously -- none of which this harness
  currently covers.
- Whether a fourth gate that doesn't exist yet (e.g., a visa-timeline
  edge case beyond a simple 0/1 factor) would also behave correctly --
  this harness only tests the three gates that exist today.

## Dependencies
- scripts/score/role-scorer.mjs -- the component under test.
- Node.js (no external npm packages beyond what the repo already installs).
- No dependency on data/ats/, private/, or any real company data -- the
  harness is entirely self-contained and uses only synthetic, clearly
  labeled test roles.

## Annotated Commands
```
node scripts/gates/gate-behavior-harness.mjs
```
This single command does everything: writes the synthetic test roles,
calls role-scorer.mjs on them, reads back the results, and prints a
PASS/FAIL table plus a final verdict and exit code. There is no
interactive step and no configuration file to edit -- the test roles are
intentionally hardcoded in the script (see "Failure Modes" below for why
that's also a limitation).

## What It Produces
- data/examples/gate-behavior-harness-input.json -- the 4 synthetic test
  roles, regenerated fresh on every run.
- data/examples/role-scores.json -- the scorer's full arithmetic trace
  for each synthetic role (this file is overwritten by role-scorer.mjs on
  every run -- it is not a growing log).
- data/examples/gate-behavior-harness-report.md -- human-readable
  Markdown table version of the same results.
- A stdout PASS/FAIL summary and a process exit code (0 = all gates
  behave correctly, 1 = a gate-as-vote bug was caught).

## Failure Modes (5, including drift and contract-violation)

1. Threshold drift. GATE_ZERO is hardcoded in the harness (0.05) to
   match CONFIG.gate_zero in role-scorer.mjs. If someone changes the
   threshold in role-scorer.mjs without updating the harness, the
   harness's assertions silently test against a stale number -- it would
   keep reporting PASS/FAIL against the old threshold, not the real one
   currently governing production scoring. This is a drift failure: two
   copies of the same constant that can silently diverge.

2. Contract violation via hardcoded synthetic data. The four test
   roles are hardcoded directly in the harness script rather than loaded
   from an external, versioned fixture file. This violates the spirit of
   this repo's data/script separation -- someone could edit the test data
   inline while "fixing a bug," inadvertently making the test easier to
   pass rather than fixing the real defect. A more disciplined version
   would load fixtures from data/examples/ as read-only input, not
   embed them in the script under test's own directory.

3. False confidence from a narrow test surface. This harness tests
   exactly one closed gate at a time. It has never verified what happens
   when two gates are closed simultaneously, or when a gate factor is
   partially closed (e.g., 0.3, between "aging" and "stale"). A
   real-world regression that only manifests under multi-gate degradation
   would pass this harness cleanly while still being broken in production.

4. Silent tolerance of borderline results. The PASS condition for a
   gated case is composite <= 0.05 -- exactly at the threshold counts as
   PASS. A regression that pushes a gated composite to precisely 0.05 (not
   fully zero, but still "passing") would not be flagged, even though a
   healthier implementation might expect gated composites to be
   effectively zero (e.g., <0.01), not merely under the Skip cutoff.

5. No coverage of the scorer's override path. role-scorer.mjs
   supports a human override that can reverse the machine recommendation
   with a documented reason. This harness never tests whether a closed
   gate's Skip recommendation can still be legitimately overridden by a
   human, or whether the override path itself has any drift risk. That is
   a real, untested interaction between two separate pieces of this
   engine's logic.