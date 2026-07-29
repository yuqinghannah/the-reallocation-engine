# Data Validation & the GIGO Gate — ux-designer-sponsor-triage

## Skeptical EDA (real output, `gigo_eda.py` run against `SEC_DOL_H1b_data_mapped.csv`)

​```
Total data rows: 30369
Rows with BLANK top_job_titles_sponsored: 28812 (94.9%)
Rows with BLANK Total Approvals: 28812 (94.9%)
Companies WITH sponsorship titles    — n=1047,  avg age = 8.8 years
Companies WITHOUT sponsorship titles — n=23688, avg age = 7.4 years
Duplicate company names: 0
Snapshot-date / "data pulled on" field present: False
​```

## Hidden Assumption #1 — "Blank = Won't Sponsor"

The mode's natural interpretation of a blank `top_job_titles_sponsored`
field is "this company has no sponsorship history, so score it low." But
**94.9% of all 30,369 companies in this file have that field blank.** If the
engine treated blank as a negative signal, it would rank nearly every
company in the dataset as low-confidence — that is not a useful signal, it
is the dataset's default state. A blank field far more likely means "this
company has never shown up anywhere in DOL's H-1B petition data at all"
(for any role, not just design), not "this company was asked and declined."
The dataset's structure — a join between SEC Form D funding records and DOL
H-1B records — will always produce mostly-blank rows, because most
Form D-funded companies are small and never file any H-1B petition,
regardless of intent.

**Company-age check:** companies WITH sponsorship history are on average
8.8 years old vs. 7.4 years for those without — a real but modest gap
(1.4 years). This partially supports the "young/small company" hypothesis
from the Domain Justification, but the gap is smaller than expected: age
alone does not fully explain the 94.9% blank rate. The blank rate is too
large to be explained by youth alone — it is largely just "never filed,"
independent of willingness.

## Hidden Assumption #2 — No Data Vintage

There is no `snapshot_date` or `data_pulled_on` column anywhere in this
file. This means the mode cannot state how current the funding or
sponsorship data is at the moment a user runs it. A company's
`latest_funding_stage` or H-1B approval count could be a year or more stale
with no way for the tool — or the person relying on it — to know.

## Quality Standard (the gate a human could check)

A record is **allowed through** to scoring only if:
1. `company_name` is non-null and non-empty.
2. At least one of `top_job_titles_sponsored` or `Total Approvals` is
   present, **or** the record is explicitly routed to a separate
   "no-history" tier rather than being silently scored as low-confidence.
3. `latest_funding_date` is parseable as a date (not required to be recent
   — just present and valid, so the gate can flag stale entries later).

A record **fails the gate and is rejected from confident scoring** if:
- `company_name` is blank (unusable — cannot report a recommendation
  without a name).
- All of `top_job_titles_sponsored`, `Total Approvals`, and
  `latest_funding_date` are blank simultaneously (no usable signal of any
  kind — not even a funding-based fallback score is possible).

## What Fails the Gate, and What We Do About It

- **28,812 rows (94.9%) have no sponsorship-title data.** Per Hidden
  Assumption #1, these are **not rejected** — they are routed to a
  separate "No Sponsorship History" tier with an explicit label
  distinguishing "no data" from "declined." This tier is never merged into
  the "Top" or "Watch" tiers regardless of funding strength, because doing
  so would silently launder a missing-data problem into a false positive.
- **No snapshot-date field exists anywhere in the source data.** Since this
  cannot be fixed at the data layer, the mode's output report will carry an
  explicit disclaimer: "Funding and sponsorship figures reflect the most
  recent SEC/DOL records available in this file; exact data-pull date is
  unknown." This is a documented limitation, not a silent gap.