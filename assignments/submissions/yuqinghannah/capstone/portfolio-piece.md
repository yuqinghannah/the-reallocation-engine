# Gate-Behavior Harness — An Automated Regression Guard for a Job-Search Scoring Engine

**Yuqing Huang** · Product/UX Designer, targeting B2B SaaS, Fintech, PropTech, and AI products
**Contribution to:** The Reallocation Engine (open-source, evidence-first H-1B job-search tool)
**Live PR:** github.com/nikbearbrown/the-reallocation-engine/pull/50

---

## The Problem

The Reallocation Engine is an open-source tool that helps international students and early-career technical workers cut through information asymmetry in the job search — specifically, whether a company has a real history of H-1B sponsorship, whether a job posting is still live, and whether a company's funding is recent enough that it's still actually hiring.

The engine's scoring logic is built on a specific design principle: certain conditions — a dead job posting, a company with stale funding — should act as **hard gates** that zero out a candidate's score entirely, not soft penalties that merely lower it. The distinction matters enormously to the person on the other end: a "70% match, but the posting is dead" recommendation is actively harmful, because it sends someone to spend hours polishing an application for a role that no longer exists.

The failure mode this project targets has a name in the engine's own documentation: the **"gate-as-vote bug"** — a coding mistake where a gate that's supposed to multiply the score (and thus zero it when closed) accidentally gets wired in as an additive vote instead. This kind of bug is dangerous specifically because it's invisible: the code runs, produces a plausible-looking number, and nothing crashes. Before this contribution, nothing in the codebase automatically checked for it.

## What I Built

I built an automated test harness — `gate-behavior-harness.mjs` — that constructs synthetic test cases with deliberately high scores, closes one scoring gate at a time, and asserts that the final score is reduced to (effectively) zero regardless of how strong the underlying votes are. If a gate ever fails to zero the score, the harness exits with a non-zero status and a printed diagnosis, so the failure surfaces immediately instead of shipping silently.

This sits on top of separate, already-submitted work where I built and tested two of the engine's real scoring gates — a **liveness gate** (checks whether a job posting is still live, using real browser automation against real URLs) and a **funding-recency gate** (checks whether a company's most recent funding round is recent enough to still be actively hiring, using real SEC/DOL sponsorship data). This capstone contribution adds the missing piece: an automated proof that both gates — plus the pre-existing timeline gate — actually behave the way the engine's design requires.

```
Architecture:

  synthetic test roles (high votes, one gate closed at a time)
              │
              ▼
     role-scorer.mjs (the component under test)
              │
              ▼
   composite score + arithmetic trace (JSON)
              │
              ▼
  gate-behavior-harness.mjs asserts: composite ≈ 0?
              │
              ▼
        PASS / FAIL + exit code
```

## The Measurable Improvement

**I deliberately reintroduced the exact bug this harness is designed to catch, and confirmed the harness catches it.**

I changed one line in the scoring engine — the operator that combines vote strength with gate status, from multiplication to addition — simulating the precise regression the book names as the capstone's representative build failure. Before the fix, 3 of 4 gated test cases that should have scored ~0 instead scored 0.57–0.62 — high enough that a real candidate could have been told to apply to a role with a dead posting or catastrophically stale company funding. After reverting the bug, all 4 cases correctly returned to a near-zero score.

| | Composite score (should be ~0) | Result |
|---|---|---|
| Correct code (gate = multiplier) | 0, 0, 0.0285 | 4/4 correctly gated |
| Bug reintroduced (gate = additive vote) | 0.57, 0.57, 0.62 | 3/4 silently passed through |
| Bug reverted | 0, 0, 0.0285 | 4/4 correctly gated again |

This is the number that makes the contribution real: **a bug that would have produced dangerously wrong recommendations was caught by this harness, on demand, every time it was reintroduced.**

## Verified vs. Inferred

Every number this contribution reports traces to one of three places: a real script execution, a real data record, or an explicitly-labeled judgment call. The full boundary table is in the attestation document, but the short version:

- **Verified (script output):** every composite score, every PASS/FAIL verdict, the arithmetic trace for how each score was computed.
- **Verified (record):** the funding dates the funding-recency gate reads come directly from a real SEC Form D + DOL H-1B joined dataset already in the engine's repository.
- **Explicitly labeled judgment, not fact:** the specific thresholds used to classify a company's funding as "fresh" vs. "stale" (≤18 months / 18–30 months / >30 months) are my own authorial choice, flagged `[VERIFY]` in the code itself — not an industry standard, and not validated against a larger sample of real hiring outcomes.

## Failure Modes (and the One I Can't Verify)

I documented five specific failure modes for this contribution — including a **drift risk** (the harness hardcodes a threshold constant that must be kept in sync with the scoring engine's own copy of the same number, and nothing currently enforces that they match) and a **contract-violation risk** (the test data is hardcoded directly in the test script rather than loaded from an external, version-controlled fixture file, which makes it too easy to "fix" a failing test by quietly editing the data instead of the underlying bug).

**The one limitation I can't verify:** this harness proves the scoring *mechanism* works correctly — that a closed gate genuinely zeroes a score rather than merely discounting it. It says nothing about whether the specific numeric thresholds behind those gates are the *right* thresholds for real hiring decisions. A gate that multiplies perfectly but is tuned to the wrong cutoff would pass every test in this harness while still giving a real job-seeker bad advice. That's a business judgment this tool hands back to a human, not something code can check.

## Demo

- **Live PR:** github.com/nikbearbrown/the-reallocation-engine/pull/50
- **Run it yourself:** `node scripts/gates/gate-behavior-harness.mjs` (no setup beyond Node.js — all test data is synthetic and self-contained)
- **Full honest-run writeup**, including the real terminal output of the bug injection and fix, is in the PR's linked worked-run document.