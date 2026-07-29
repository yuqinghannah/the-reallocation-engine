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
## Reflection (after building)

**What actually happened:** My prediction about survivorship bias was
confirmed — the GIGO gate found 94.9% of companies have blank sponsorship
history, and the Bias Audit confirmed young/early-stage companies are
selected into usable tiers at roughly 1/9th to 1/11th the rate of
mature/late-stage ones. So that part of my prediction was right.

**Where my prediction was wrong:** I did not predict the two failures that
turned out to matter more in practice. First, the Adversarial Robustness
test found that 5 real companies — including a well-known name, `FIGMA
INC` — landed in the highest-trust "Top" tier based entirely on a
design-adjacent-but-different title (e.g., "Motion Designer, Brand
Studio"), not a genuine Product/UX Designer sponsorship record. Second, and
more surprising to me, the funding-recency check showed that 90% (64 of
71) of "Top" tier companies have funding data more than 2 years old — some
over a decade stale. I expected the causal weakness to come from the
approval-rate signal being confounded (which it was — approval rate turned
out to be nearly flat, 96.9%-98.5%, across every company size, so it barely
discriminates at all), but I did not expect the funding-stage signal itself
to be resting on data this old for the large majority of my top
recommendations.

**What this says about my calibration:** I was right about the general
shape of the problem (the tool can't tell "no signal" from "no interest")
but I underestimated how much of the tool's apparent confidence — high
scores, "High" confidence labels — was actually resting on stale or
mismatched inputs rather than genuinely strong evidence. My 7/10 confidence
in my own prediction was reasonable for the part I got right, but I was
overconfident about having already found the main risk before I'd actually
run the checks. The lesson I'm taking from this: a prediction based on
reading my own prior work (the Domain Justification) felt more solid than
it should have, because it hadn't yet been tested against the full,
unfiltered real data — running the actual numbers surfaced problems I
would not have found by reasoning alone.