# Build It, Then Break It: A Skeptic's Portfolio
**Yuqing Huang · INFO 7375 · Computational Skepticism for AI**

---

## 1. The Artifact

**What it is:** `score_companies.py`, the H-1B visa sponsorship-triage scoring
tool originally built and submitted for "The Reallocation Engine, Audited"
(July 29). It ranks 30,369 companies by a composite 0–100 score combining:
design-title sponsorship history (40 pts), historical H-1B approval rate
(35 pts), and latest funding stage (25 pts), then buckets each company into
a tier (Top / Watch / Low Priority / Insufficient Data) and a stated
confidence (High / Medium / Low).

**Why reuse it here:** this assignment asks the builder to audit their own
work. Reusing an artifact I already built and fully understand — rather
than building something new and smaller just for this assignment — is a
more honest test of the assignment's actual claim ("a builder is the least
reliable auditor of their own build"), since I have every incentive to
believe this tool already works.

**Data:** `SEC_DOL_H1b_data_mapped.csv` — 30,369 U.S. companies, joining
SEC Form D funding filings with DOL H-1B petition history. Same real data
used in the original assignment; no synthetic rows.

**Run / repro note:**
```
python score_companies.py          # original tool, unchanged
python build_calibration_dataset.py  # produces calibration_dataset.csv
python calibration_analysis.py       # Instrument 1
python dataframe_audit.py            # Instrument 2
```
All four scripts live in the project root, alongside `SEC_DOL_H1b_data_mapped.csv`
under `data/80-days-to-stay/data/`.

**Pre-registered suspect decision (logged before running any instrument,
2026-08-09):** The 40/35/25 point split across design-match, approval
rate, and funding stage was chosen by feel, not fit to any real outcome
data. I was least sure of this weighting — it could just as easily have
been 30/40/30 or any other split, and nothing in the build process ever
checked whether these weights track anything real. I flagged this as the
most likely place a mistake was hiding.

---

## 2. Instrument 1 — Calibration (Ch. 2 + Ch. 11)

### Prediction-lock (dated 2026-08-09, before running calibration_analysis.py)
"The High-confidence bucket requires `total_decisions >= 3 AND design_match`,
both of which are mechanically related to whether a company has decision
data at all. I predict the reliability diagram will look artificially good
(points near the diagonal) — not because the tool has real predictive
skill, but because of this circularity — and I predict the High bucket
will have very few rows."

### Method
1. Recomputed the tool's existing stated confidence (Low/Medium/High) for
   every row, unchanged from the original logic.
2. Mapped confidence → a claimed probability: High=0.9, Medium=0.6,
   Low=0.3. This mapping is my own operationalization — the tool never
   states a number — done explicitly so the label could be tested.
3. Ground truth: whether the company has any real DOL decision on record
   (`Total Approvals + Total Denials > 0`) — a directly observable fact
   in the source data, not fabricated.
4. Computed Brier score, ECE, and a full reliability diagram
   (`reliability_before.png`).
5. Fit a single temperature parameter via grid search, re-plotted
   (`reliability_after.png`).
6. Re-ran the same test on the blank-funding-stage slice, using the
   temperature fit on the full data, to test for distribution shift
   (`reliability_shift_blank_stage.png`).

### Result
```
Sample sizes:      Low = 0 rows   Medium = 1,496 rows   High = 61 rows
BEFORE:  Medium claimed=0.60 actual=1.0000 | High claimed=0.90 actual=1.0000
         Brier = 0.1541   ECE = 0.3882
AFTER (T=0.05): Medium claimed_avg=0.9997 actual=1.0000 | High claimed_avg=1.0000 actual=1.0000
         Brier = 0.0000   ECE = 0.0003
Blank-stage slice (n=20): claimed_avg=0.9997  actual=1.0000  Brier=0.0000  ECE=0.0003
```

**My prediction was wrong, but in a worse direction than I expected.** I
predicted mild circularity and a small High bucket. What actually happened:
the **Low bucket had zero rows**, and both remaining buckets had an
actual rate of exactly 1.0000. That is not "somewhat correlated with
having decision data" — it is a tautology. `total_decisions >= 1` is
literally part of the definition of Medium/High confidence, and I chose
`total_decisions > 0` as my ground truth. I built a test that could not
fail. The "perfect" post-calibration ECE of 0.0003 is not evidence the
tool predicts anything; it is evidence I measured the same fact against
itself. The distribution-shift slice looking identical to the full data
confirms this — a broken calibration test has no ability to distinguish
subpopulations, so of course it showed "no shift."

**Descartes' move applied here:** how could this confident-looking result
(near-diagonal reliability, ECE≈0) be false? Answer: it can be false in
the sense that matters — it can look this good while measuring nothing —
if the "prediction" and the "outcome" are drawn from overlapping
definitions. That is exactly what happened.

**Plato's move applied here:** the artifact I made is a *stated confidence
label*. The world it claims to describe is *whether this company will
actually sponsor a design H-1B in the future*. The relationship I actually
tested was neither of these — it was the relationship between "does this
row have decision data" and "does this row have decision data," under two
different names.

---

## 3. Instrument 2 — Data-Frame Audit (Ch. 3)

### Prediction-lock (dated 2026-08-09, before running the full-data scan)
"Non-blank `latest_funding_stage` values will contain strings unrecognized
by `FUNDING_STAGE_SCORE` (e.g. 'IPO', 'Growth'), and these will be
silently scored as `stage_score=0`, artificially depressing scores for an
unknown but nontrivial number of well-funded companies."

### Method
1. Datasheet-style structural check on the full 30,369-row file: enumerated
   every distinct value in `latest_funding_stage`.
2. Structural-assumptions table (below).
3. Traced one real row (23ANDME INC) end-to-end through every branch of
   `score_row()`.
4. Plant-and-find: quantified how many companies are affected by treating
   blank funding-stage the same as the worst known stage, and how many
   would actually change tier under a version that excludes blank stage
   from the funding term instead of zeroing it.

### Result — prediction disconfirmed, but a related bug found
All six known stage strings (Pre-Seed, Seed, Series A/B/C/D+) were
recognized with zero unmatched non-blank values across all 30,369 rows.
**My specific prediction was wrong.**

What I found instead: **2,495 rows (8.2%) have a *blank* `latest_funding_stage`**,
and the code's `FUNDING_STAGE_SCORE.get(stage_raw, 0)` treats blank the
same way it would treat an unrecognized string — both silently become
`stage_score=0`, indistinguishable from "the worst known funding stage."
This conflates *unknown* with *bad*, which is exactly the kind of
MNAR (missing-not-at-random) problem the tool's own GIGO gate was built
to catch for sponsorship data, but was never applied to funding data.

**However, quantifying the actual impact matters, and I did not assume
severity — I measured it:** of the 30,369 rows, only 20 have a blank
funding stage *and* enough other data to be scored at all (most blank-stage
companies are also missing sponsorship data and get caught by the
existing GIGO gate before funding stage ever matters). Of those 20, **zero
companies (0.0%) change tier** under a fixed version that excludes the
funding term for blank-stage rows instead of zeroing it.

**Hume's move applied here:** this 0-out-of-20 result is a fact about
*this specific dataset, at this specific snapshot in time* — it is not a
general claim that the bug is harmless. A different data pull, or the
same data six months from now with more blank-stage rows crossing tier
thresholds, could show a different result. My confidence here is about my
sample, not about the world.

### Structural assumptions table

| Dimension | Assumption made | Risk if wrong |
|---|---|---|
| Sampling | 30,369 companies with any SEC Form D + DOL H-1B match are representative of the design-sponsorship market | Selection bias toward VC-funded, larger companies; excludes companies that sponsor without ever raising Form D funding |
| Time window | Single snapshot join; no explicit "as-of" date per field | Funding stage and approval history may be recorded at different points in time for the same row |
| Label proxy | `top_job_titles_sponsored` used as a full proxy for "does this company sponsor design roles" | Field appears to be a truncated top-N list (e.g. 23ANDME shows exactly 1 title, 6SENSE shows 2) — see one-row trace below — so real design sponsorship can be invisible to this feature |
| MNAR | Blank `latest_funding_stage` (8.2%) treated identically to worst known stage | Conflates "we don't know" with "this company is doing badly," as confirmed above |
| Feature engineering | Composite score weights (40/35/25) chosen without validation | Arbitrary; see Step 1 pre-registered decision |
| Boundary | Tier cutoffs at 65 / 35 are fixed constants | No sensitivity analysis on whether small shifts in the cutoff change tier membership meaningfully |

### One-row trace (23ANDME INC)
```
Raw top_job_titles_sponsored: ['Senior Data Engineer']  (single title listed)
Raw Total Approvals: 52.0   Raw Total Denials: 2.0
Raw latest_funding_stage: Series C   Raw latest_funding_date: 2020-12-09

Step 1 — design_match = False
  (the titles field lists only one job title for a company that has
  52+2=54 recorded H-1B decisions total — it is very unlikely this
  company sponsored only one distinct role across 54 petitions. This
  strongly suggests top_job_titles_sponsored is a truncated top-N list,
  not a full history, which is the label-proxy risk flagged above.)
Step 2 — approval_rate = 52 / 54 = 0.9630
Step 3 — stage_raw = 'series c' -> stage_score = 5 (out of 6)
Step 4 — score = 0 (no design match) + 33.7 (approval) + 20.8 (funding) = 54.5
Step 5 — tier = Watch
```
23ANDME lands in "Watch," not "Top," entirely because of the design-match
false negative — not because it lacks real H-1B activity. This is the same
truncated-title-list risk named in the structural-assumptions table,
observed directly on a real row rather than only inferred statistically.

**Popper's move applied here:** before running the scan, I decided in
advance that finding any unmatched non-blank stage string would count as
confirming my prediction, and finding none would count as disconfirming
it. None were found — the prediction failed by its own pre-registered
standard, cleanly, without me reframing "no unmatched values" as a partial
win after the fact.

---

## 4. The Confession — Where I Let the Mistake In

**What the mistake was:** In designing the Calibration instrument, I chose
a ground-truth label — "does this company have any real DOL decision on
record" — to test against the tool's stated confidence. I did not notice,
until after building the full pipeline (dataset builder, reliability
diagrams, Brier score, ECE, temperature-scaling fit), that this label is
*definitionally* entailed by the confidence categories themselves: Medium
and High confidence are only assigned when `total_decisions >= 1`, and my
ground truth was `total_decisions > 0`. I built a calibration test that
was mathematically guaranteed to show "perfect" calibration regardless of
whether the tool has any real skill.

**Why I wanted to believe the version that contained it:** I designed,
coded, and ran this whole pipeline myself, end to end, in one sitting. By
the time the numbers came out — a clean reliability diagram, a Brier score
that dropped to 0.0000 after temperature scaling — it *looked* like a
successful, well-executed calibration analysis. I had already invested in
building matplotlib plots and a working temperature-scaling fit; the
fluency I was defending was "I designed a working calibration pipeline,"
not "this specific ground-truth choice is sound." A working pipeline and a
valid experiment are not the same thing, and I conflated them.

**How I caught it:** the tell was a result too good to be plausible — the
Low-confidence bucket had exactly zero rows, and both remaining buckets
showed an actual outcome rate of precisely 1.0000, not 0.97 or 0.94. Real
calibration on a genuinely predictive signal almost never lands on an
exact integer like that across two independent buckets. Rereading my own
`build_calibration_dataset.py`, I saw that the confidence-assignment logic
and the ground-truth logic both keyed off `total_decisions`.

**What I changed:** I did not silently patch the ground truth and re-run
without flagging it — I am reporting the tautology itself as the finding,
because the assignment's honesty floor asks for the real mistake, not a
retroactively cleaned-up version of the analysis. If I were to fix this
properly, the ground truth would need to be something the confidence
label does not already encode by definition — for example, whether the
*approval rate specifically* (not mere presence of decisions) exceeds some
threshold, computed only on the subset that already has decision data, so
the two quantities are no longer mechanically linked.

**Residual risk:** even a "fixed" ground truth built from the same 1,557
rows with real decision data is still a small, non-random subset (5.1% of
the full dataset) — likely larger, more established companies that happen
to have public H-1B decision records. Any calibration result on that
subset would not generalize to the other 94.9% of companies the tool also
scores. A genuinely sound calibration test for this tool would need
outcome data this dataset does not contain: whether each company *actually
sponsored a design hire in the future*, which no snapshot join can supply.

---

## 5. Closing — What Would Change My Mind / Still Puzzling

**What would change my mind about the calibration finding:** if someone
rebuilt the ground truth from a field with no shared derivation from
`total_decisions` — e.g., an independent future-dated outcome — and the
reliability diagram still showed near-perfect calibration with a
reasonably sized Low bucket, I would take that as real evidence, not an
artifact of definition overlap.

**Still puzzling:** the design-match false-negative risk (Section 3,
23ANDME trace) is not fully resolved here — I don't know how many of the
30,369 companies are silently mis-classified because their real design
hires fall outside a truncated top-N title list, only that it's
structurally possible and observed on at least one real row. Quantifying
that properly would require access to full per-company petition-level
data, not the aggregated snapshot this dataset provides.
