# Causal & Counterfactual Reasoning — Pearl's Three Rungs
## ux-designer-sponsor-triage

## Rung 1 — Observation: What Correlates With a "Good Outcome"?

The tool's score treats three things as positively correlated with "will
sponsor a designer": (1) a matched design-title in H-1B history, (2) a high
historical approval rate, (3) a later funding stage. Real data confirms
correlations #1 and #3 are present — the Bias Audit already showed later-
funding-stage companies are ~10.8x more likely to land in a usable tier.

But a closer check of correlation #2 (approval rate) produces a surprising
result:

```
=== APPROVAL RATE AND VOLUME BY FUNDING STAGE (companies with any decisions) ===
pre-seed   n=138  avg_approval_rate=96.9%  avg_total_approvals_per_company=32.3
seed       n=189  avg_approval_rate=98.2%  avg_total_approvals_per_company=20.3
series a   n=332  avg_approval_rate=97.4%  avg_total_approvals_per_company=21.5
series b   n=364  avg_approval_rate=98.5%  avg_total_approvals_per_company=85.8
series c   n=265  avg_approval_rate=97.8%  avg_total_approvals_per_company=93.3
series d+  n=249  avg_approval_rate=98.2%  avg_total_approvals_per_company=208.3
```

**Approval rate is nearly flat across every funding stage (96.9%–98.5%, a
1.6-point spread)** — U.S. H-1B petitions are approved at a consistently
high rate across almost all filers once submitted, regardless of company
size. What actually scales dramatically with funding stage is **approval
volume** (32 at pre-seed vs. 208 at Series D+, a ~6.4x increase) — i.e.,
bigger, later-stage companies simply file more petitions across their
entire workforce, not because they are more "reliable" sponsors per se.

**Observation-rung conclusion:** the tool's `approval_rate` scoring
component (35 of 100 points) is, in practice, rewarding almost every
company that has any filing history nearly equally, since the rate barely
varies. The real driver of tier placement is company *scale* (funding
stage + total hiring volume), which correlates with — but is not the same
thing as — willingness to sponsor a design-specific hire.

## Rung 2 — Intervention: Is the Engine Optimizing an Interventional Quantity?

**No.** The engine estimates *P(this company has historically sponsored a
design-adjacent H-1B role)* — a purely retrospective, observational
quantity. The actual question a job-seeker needs answered is
interventional: *"If I apply my limited time to Company X, does that
increase my probability of receiving a sponsored offer, compared to
applying elsewhere?"* These are not the same question, and a real
confounder sits between them:

**Confounder — Company-wide hiring scale.** A Series D+ company's high
approval *volume* (208 avg.) mostly reflects overall headcount growth
across every department (engineering, sales, ops), not a specific
willingness to sponsor a *design* hire. If the underlying driver of "gets
placed in Top tier" is really "is a large company that hires and sponsors
constantly, for any role" — a variable this dataset does not isolate —
then the observed correlation between funding-stage/approval-volume and
"design-sponsorship-friendly" would likely shrink or vanish once company-
wide headcount is controlled for. A small company with 2 total approvals,
both for design roles, could be genuinely more design-sponsorship-
committed per capita than a giant company with 208 approvals spread across
every function — but the current score cannot see that distinction,
because it only has aggregate counts, not departmental breakdowns.

**Confounder — Time-varying policy environment.** The GIGO gate already
found there is no snapshot date on this data. H-1B approval rates and
lottery odds shift with USCIS policy and annual cap changes. A company's
historical approval record from several years ago may not reflect current-
year sponsorship conditions — the intervention (applying today) happens in
a different policy environment than the one the historical data describes.

## Rung 3 — Counterfactual

**Specific case:** `ADDEPAR INC` — Top tier, score 100.0, confidence High,
150 real approvals, 0 denials, Series D+.

**Counterfactual question:** Suppose a job-seeker followed this tool's
recommendation and spent 70% of their application-writing time on Top-tier
companies like `ADDEPAR INC`, instead of splitting effort equally across
all 1,536 companies with any sponsorship data (the no-tool baseline). Would
this reallocation have actually increased their odds of a sponsored offer?

**Assumptions this counterfactual rests on** (stated explicitly, not
hidden):
1. That probability of receiving an offer *per hour of applied effort* is
   independent of how competitive/prestigious the company is. This is
   likely **false** — large, well-known, well-funded companies like
   `ADDEPAR INC` typically draw far more applicants per opening, so the
   per-hour probability of even landing an interview may be *lower*, not
   higher, than at a smaller, less-visible Series B company — even though
   the company's historical approval rate, once hired, is high.
2. That the historical approval "stock" (accumulated over years) reflects
   this year's real openings and sponsorship budget. This cannot be
   verified — there is no data-vintage field (GIGO gate finding).
3. That a higher approval *rate* meaningfully predicts a better outcome.
   Rung 1 showed this rate is nearly flat (96.9%–98.5%) across every
   company size — so it carries very little real discriminating
   information, despite being weighted at 35 of 100 score points.

**Since assumption #1 is probably false and assumption #3 is empirically
weak (the "signal" barely varies), the counterfactual claim — that
following this tool's reallocation recommendation causes a better
sponsorship outcome for this specific applicant — cannot be honestly
asserted with confidence.**

## Honest Verdict

**This engine reallocates predominantly on correlation dressed as
causation.** It optimizes an observational, retrospective quantity —
historical approval volume and funding stage, both of which are more
plausibly proxies for *overall company hiring scale* than for
*design-specific sponsorship willingness* — and presents it as an
actionable recommendation ("spend your time here"). The dominant
confounder — total company headcount/hiring volume, which this dataset
does not isolate from design-specific sponsorship activity — could shrink
or eliminate the observed correlation if it were possible to control for
it. Per the assignment's own framing: most reallocation engines do this,
and the honest thing to do is name it plainly rather than claim causal
validity the tool has not earned.