# Frictional Journal — ux-designer-sponsor-triage (Audited)

## Prediction (before building)
**Timestamp:** 2026-07-28 15:35 (America/Los_Angeles)

**Expected hardest-to-catch failure:** Survivorship bias in the sponsorship
history — a company with zero H-1B filings for any design-adjacent title
will likely get scored as "won't sponsor," when in reality it may simply
have a small or newly-formed design team that has never yet needed to
sponsor one. This is the failure I'd expect to be hardest to catch because
"no history" and "unwilling" produce an identical signal in the data — there
is no field that distinguishes "asked and said no" from "never asked."

**Expected causal validity:** Medium. The engine's core signal (past H-1B
sponsorship of a design-titled role) plausibly correlates with willingness
to sponsor again, but I expect this to be confounded by company size,
funding stage, hiring-budget cycles, and immigration-policy shifts between
when the historical filing was made and today. I don't expect the engine to
cleanly separate "this company sponsors designers" (a durable trait) from
"this company sponsored one designer once, under conditions that may no
longer hold" (a point-in-time event).

**Confidence:** 7/10 — based on having already run this data once (Worked
Run, 2026-07-06) and having already hand-identified the survivorship-bias
concern in the Domain Justification before this assignment existed. This
isn't a cold guess; it's informed by direct exposure to the dataset's
structure (`top_job_titles_sponsored` as a flat historical list with no
recency weighting or team-size normalization).

---

## Reflection (after building)
*[To be completed after the tool, GIGO gate, bias audit, causal analysis,
and adversarial test are done — filled in at the end, not now.]*