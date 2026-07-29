# Bias Audit (Data → Output) — ux-designer-sponsor-triage

## Quantitative Fairness Metric: Selection Rate / Disparate Impact Ratio

"Selection rate" here = the proportion of companies in a group that the
tool routes into a *usable* tier (Top or Watch), as opposed to
"Insufficient Data." This mirrors the standard "four-fifths rule" used in
employment discrimination law: a selection-rate ratio below 0.80 between
groups is treated as evidence of disparate impact.

### By Company Age
```
Unknown Age     n=5634   usable=503  rate=8.93%
Young (<3 yrs)  n=2496   usable=15   rate=0.60%
Mid (3-8 yrs)   n=9954   usable=373  rate=3.75%
Mature (8+ yrs) n=12285  usable=645  rate=5.25%
```
Excluding the "Unknown Age" bucket (an artifact — likely large companies
missing incorporation-date data, not a real age group): **Young companies
are selected at 0.60%, Mature companies at 5.25% — a ratio of 0.114,
about 8.75x lower for young companies.**

### By Funding Stage
```
Early (Pre-Seed/Seed)   n=15983  usable=316  rate=1.98%
Unknown/Blank Stage     n=2495   usable=17   rate=0.68%
Growth (Series A/B)     n=9496   usable=689  rate=7.26%
Late (Series C/D+)      n=2395   usable=514  rate=21.46%
```
**Early-stage companies are selected at 1.98%, Late-stage at 21.46% — a
ratio of 0.092, about 10.8x lower for early-stage companies.** In absolute
terms this is the larger gap: a 19.5-percentage-point spread, versus a
4.65-point spread for age.

**Comparison verdict:** funding stage produces the larger disparity, both
in ratio and in absolute terms. Company age matters, but funding stage is
the dominant driver of who gets excluded from a usable recommendation.

## Where the Bias Enters (mechanism)

This is not only a data-availability problem — it is **compounded by the
scoring formula itself**. The composite score directly awards up to 25 of
100 points based on `latest_funding_stage` (Series D+ = full 25 points,
Pre-Seed ≈ 4 points). So even among companies that *do* have sponsorship
history, an early-stage company starts 21 points behind a late-stage one
before any sponsorship signal is considered. The bias enters at two
points: (1) the underlying data — small/young/early companies are
structurally less likely to have filed any H-1B petition yet (the GIGO
gate finding), and (2) the scoring formula, which then further penalizes
exactly the companies already disadvantaged by (1).

## Two Fairness Definitions in Tension

**Definition A — Demographic Parity:** young/early-stage companies should
be routed into usable tiers (Top/Watch) at a rate similar to mature/late-
stage companies, regardless of how little sponsorship history exists for
them yet.

**Definition B — Calibration (equal predictive meaning):** a given score or
tier should mean the same thing regardless of company age or funding
stage — i.e., "Top" should reflect genuinely strong evidence, not a
lowered bar applied unevenly to make the tiers look demographically even.

**The tradeoff:** These two cannot both be satisfied here. Enforcing
Demographic Parity would require either inventing confidence for young/
early companies that the data does not support (directly violating the
GIGO gate's rule that a blank field is reported as "insufficient data,"
never guessed at) — or artificially suppressing mature/late-stage scores
to force parity, which would throw away real, verified signal. Enforcing
Calibration (what this tool currently does) keeps every score honest, but
it means young and early-stage companies will, as a group, continue to be
statistically underrepresented in the "Top"/"Watch" tiers — even though
some of them may be exactly the kind of small, hungry team most willing to
sponsor a specific designer once they actually hire one (the concern
raised in the original Domain Justification).

**Chosen position:** this tool prioritizes Calibration over Demographic
Parity, because inventing sponsorship confidence for companies with zero
real history would violate the honesty principle the whole engine is
built on (P5 / the GIGO gate). But this is a real cost, not a free choice
— it is documented here rather than resolved away.

## Highest-Leverage Intervention Point

The highest-leverage fix is **not** the composite scoring formula itself —
patching weights there just moves the disparity around without addressing
its source. The highest-leverage point is the **"Insufficient Data" tier's
internal structure**. Currently it is one flat, undifferentiated bucket
(94.9% of all companies). Splitting it using the *same* age/funding signals
— but as a **qualifier on top of "no data," not as a scoring input that
locks companies out of Top/Watch** — would let the tool say, honestly:
"No sponsorship history AND young/early-stage → worth direct outreach,
absence of data is not evidence of unwillingness" versus "No sponsorship
history AND mature/late-stage → longer track record with no H-1B activity
at all, lower expected upside." This preserves Calibration (no score is
invented) while giving young/early companies a differentiated, honest
signal instead of being flattened into the same undifferentiated
"Insufficient Data" label as everyone else.