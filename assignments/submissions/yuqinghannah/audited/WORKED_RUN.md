# Worked Run — The Working Reallocation Tool (Audited)

## Objective (one plain sentence)
Rank companies by estimated likelihood of sponsoring a Product/UX Designer
H-1B, using historical design-title sponsorship approval rate, funding
health, and company age, so a design job-seeker can reallocate limited
application time toward companies most likely to sponsor.

**What this leaves out:** whether the company is actively hiring for a
sponsored role right now, whether it has immigration-sponsorship budget
this specific year, and whether the applicant's own qualifications match
the role. Past sponsorship of a title is not a guarantee for a specific
future hire.

## Command run
```
python assignments\submissions\yuqinghannah\audited\score_companies.py
```

## Real output (pasted, not described)
```
=== TIER DISTRIBUTION (all 30,369 companies) ===
Insufficient Data: 28812 (94.9%)
Watch: 1465 (4.8%)
Top: 71 (0.2%)
Low Priority: 21 (0.1%)

=== SAMPLE: TOP 10 SCORED COMPANIES (Tier = Top) ===
ADDEPAR INC                         score=100.0  confidence=High
  reason=has design-title H-1B history; approval rate 100%; funding stage series d+
AMBIENCE HEALTHCARE INC              score=100.0  confidence=High
GEMINI SPACE STATION LLC             score=100.0  confidence=High
HIGHSPOT INC                         score=100.0  confidence=High
MERCURY TECHNOLOGIES INC             score=100.0  confidence=High
PARTICLE MEDIA INC                   score=100.0  confidence=High
SENDBIRD INC                         score=100.0  confidence=High
SKIMS BODY INC                       score=100.0  confidence=High
UNITE USA INC                        score=100.0  confidence=High
PALANTIR TECHNOLOGIES INC            score=99.7   confidence=High

=== SAMPLE: 5 'Insufficient Data' companies (should NOT be read as 'no') ===
$AVY INC          tier=Insufficient Data confidence=Low
011235813 INC     tier=Insufficient Data confidence=Low
0XCORD INC        tier=Insufficient Data confidence=Low
0XESSENTIAL INC   tier=Insufficient Data confidence=Low
1 KICKER HOLDINGS LLC  tier=Insufficient Data confidence=Low

=== BREAK ATTEMPT: Top-tier companies with confidence != High ===
Found 10 of 71 Top-tier companies with confidence below High.
AMAZEVR INC        score=91.7  confidence=Medium  funding stage series b
REVEL SYSTEMS INC  score=91.7  confidence=Medium  funding stage series b
YENDO INC          score=91.7  confidence=Medium  funding stage series b
FITLAB INC         score=87.5  confidence=Medium  funding stage series a
HM BRADLEY INC     score=87.5  confidence=Medium  funding stage series a
ORBEE INC          score=87.5  confidence=Medium  funding stage series a
RATEGRAVITY INC    score=87.5  confidence=Medium  funding stage series a
XL8 INC            score=87.5  confidence=Medium  funding stage series a
LOOPIE INC         score=79.2  confidence=Medium  funding stage pre-seed
PROBIOTIC LABS INC score=79.2  confidence=Medium  funding stage pre-seed

=== REALLOCATION RECOMMENDATION ===
Baseline (no tool): spend application-time equally across all 1536
companies with any data.
Recommended reallocation: move effort so that ~70% of application-writing
time goes to the 71 'Top' companies, ~25% to the 1465 'Watch' companies,
~5% held as exploratory outreach to well-funded 'Insufficient Data'
companies (since absence of history there is not evidence of unwillingness).
Uncertainty flag: 10 of the 71 'Top' recommendations rest on thin evidence
(confidence=Medium, not High) — treat these as lower-confidence within the
Top tier, not equal to the confidence=High ones.
```

## Verified vs. Inferred
**Verified (directly from the tool's own output, not my interpretation):**
tier counts (28,812 / 1,465 / 71 / 21), the specific companies and scores
listed above, the 10-of-71 thin-evidence count, `ADDEPAR INC`'s raw
`Total Approvals=150.0, Total Denials=0.0` (checked against the raw CSV row
directly with `Select-String`, not just the script's math).

**Inferred (my judgment layered on top of verified numbers):** that a 1.4
year average-age gap between "has history" and "no history" companies
(from the GIGO EDA) is too small to fully explain the 94.9% blank rate on
its own — I have not run a formal statistical test on this, it's a
reasoned read of the numbers, not a proven causal claim.

## Break Attempt (Attestation requirement)
I suspected the scoring formula might let a company with a fluke small
sample (e.g., 1 approval, 0 denials = 100% approval rate) score identically
to a company with a large, robust approval history (e.g., 150 approvals).
I checked the #1-ranked company (`ADDEPAR INC`) against the raw CSV row and
confirmed it has 150 real approvals, 0 denials — not a fluke. I then
widened the check to the full Top tier and found the confidence field
**does** catch the thinner cases: 10 of 71 Top-tier companies are flagged
`confidence=Medium` rather than `High`, meaning the tool already separates
"high score" from "high evidence" rather than treating a 100% approval rate
the same regardless of sample size. This is a real, useful finding — it
shows the uncertainty layer is doing real work, not decoration — and it's
also a limitation worth stating plainly: **within the "Top" tier itself,
confidence still varies, and a user skimming only the tier label (not the
confidence field) could over-trust a Medium-confidence "Top" company.**

## Attestation
- Recipe: score_companies.py v1.0 (Audited assignment)
- By: Yuqing Huang · 2026-07-28

### Tested
| Ran | Saw | Expected |
|---|---|---|
| `python score_companies.py` (full run, 30,369 rows) | Ran cleanly, tier counts sum to 30,369 | Some usable output; did not know exact tier sizes in advance |
| Manual check of `ADDEPAR INC` raw CSV row (deliberate break attempt) | 150 real approvals, 0 denials — not a fluke | Was checking for a possible small-sample-size flaw |
| Check of confidence field across all 71 Top-tier companies | 10/71 flagged Medium, not High | Suspected some thin-evidence cases existed; confirmed and quantified |

### Did not test
- Whether the design-title regex (`DESIGN_PATTERN`) has false positives
  (e.g., matching "Motion Graphics Designer" as if it were a Product/UX
  Designer role) — flagged in Domain Justification, not yet re-verified
  against this specific tool's output.
- Whether `latest_funding_date` recency (how many years old the funding
  round is) meaningfully changes results — the current script uses funding
  *stage*, not funding *recency*, as a scoring input; recency is
  acknowledged but not yet scored.
- Statistical significance of the 8.8-vs-7.4-year company-age gap from the
  GIGO EDA.

### Broke during testing, fixed
- Nothing broke in this run; the deliberate break attempt (checking for
  fluke high scores) did not surface a bug, but it did surface a real,
  documented edge case (10/71 Top-tier companies with Medium confidence)
  that is now explicitly flagged rather than hidden.

## Reflection
**What went well:** The tier/confidence split worked exactly as designed —
it caught real evidence-strength differences within the "Top" tier without
needing any extra code changes. The GIGO gate's "Insufficient Data" routing
also worked cleanly: 94.9% of companies were never silently scored low,
they were explicitly separated out.

**What the tool got wrong or missed:** The design-title regex is still
naive string matching (same limitation flagged in the original Domain
Justification) — it has not been re-verified against this specific
scored output. The tool also does not yet account for funding *recency*
(how many years old the last round is), only funding *stage*, which could
misrank a company that raised Series D+ five years ago as equal to one
that raised it five months ago.

**Next steps:** (1) Re-run the title-match audit specifically against the
71 Top-tier companies to check for adjacent-but-wrong title matches.
(2) Add a funding-recency penalty using `latest_funding_date`. (3) Carry
these two open issues into the Adversarial Robustness component.