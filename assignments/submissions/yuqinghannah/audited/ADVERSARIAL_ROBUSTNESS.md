# Adversarial Robustness & Fragility — ux-designer-sponsor-triage

## Perturbation Tested

**Question:** Does the tool place a company in a trusted, usable tier
(Top/Watch) based *solely* on an adjacent-discipline "design" title
(Industrial Designer, 3D Designer, Motion Designer, Architectural
Designer) — titles that match the regex string but do not represent real
Product/UX Designer sponsorship history?

This is not a hypothetical distribution shift or synthetic gamed input —
it is a real perturbation already present in the live dataset, surfaced by
running the check against all 30,369 companies.

## Result: The Tool Fails

```
=== ADVERSARIAL TEST: companies in Top/Watch backed ONLY by ===
=== adjacent-discipline 'design' titles (not real Product/UX Designer) ===
Found 5 vulnerable case(s).
AMAZEVR INC     tier=Top  score=91.7  matched_titles=['3D Designer']
APPLOVIN CORP   tier=Top  score=99.5  matched_titles=['Senior Designer, Motion Graphics']
ELROY AIR INC   tier=Top  score=87.5  matched_titles=['Industrial Designer']
FIGMA INC       tier=Top  score=99.6  matched_titles=['Motion Designer, Brand Studio']
HOME EC INC     tier=Top  score=79.2  matched_titles=['Architectural Designer II']
```

**Five real companies land in the highest-trust "Top" tier — with scores
as high as 99.6 out of 100 — based entirely on a design-adjacent title
that is not a Product/UX Designer role.** None of these companies have any
*other* matched design title backing their placement; the entire 40-point
"design match" component of their score rests on a single mismatched
string.

## Why This Case Matters Most: `FIGMA INC`

The most striking failure is `FIGMA INC`, scoring 99.6 — Figma is one of
the most recognizable names in the Product/UX design software industry.
A job-seeker seeing "Figma — Top tier — 99.6" would have every reason to
trust it without question. But the *only* evidence behind that score in
this dataset is a "Motion Designer, Brand Studio" sponsorship record — not
a Product or UX Designer title. The company's real-world reputation makes
the tool's specific claim (design-adjacent H-1B history exists) feel far
more validated than it actually is. This is exactly the kind of failure "a
human wouldn't notice" that the assignment warns about: the score and
company name together create false confidence that the underlying
evidence does not support.

## Conditions Under Which the Engine Flips

The engine flips into a false "Top" recommendation whenever:
1. A company's `top_job_titles_sponsored` field contains **at least one**
   string matching the `designer` regex, **and**
2. That string belongs to a design-adjacent-but-different discipline
   (motion, industrial, architectural, 3D), **and**
3. No other title in the same field is a genuine Product/UX Designer
   role, **and**
4. The company's approval rate and funding stage are otherwise strong
   enough to push the score into Top/Watch range.

All four conditions hold simultaneously for the 5 companies above — this
is not an edge case requiring an unusual data error; it emerges naturally
from real, unmodified data.

## Honest Limits

This adversarial test only checked for the specific adjacent-discipline
titles already identified in the Explainability audit (Part B). It has
**not** checked for other possible mismatches the same regex could catch —
for example, a title like "UX Researcher" or "UI Developer" would not
match this particular pattern, but a title like "Set Designer" (theatrical/
film production) or "Sound Designer" (audio) would match the plain
"designer" substring and has not been specifically checked against the
current Top/Watch tier. The 5 cases found here are a lower bound on this
vulnerability, not a complete count.

## What This Means for the Tool's Trustworthiness

This finding directly reinforces the Explainability critique: the
`confidence` field (based on approval count) does **not** protect against
this failure mode, since `FIGMA INC` and `APPLOVIN CORP` likely carry
`confidence: High` given their strong approval history — the tool is
confident in the wrong thing. A fix would require either (a) maintaining
an explicit allow-list of confirmed Product/UX Designer title strings
rather than a broad "designer" substring match, or (b) flagging any
company whose *only* matched title falls outside a curated allow-list as
"Unverified Match" rather than folding it into the same score as a
genuine match. Neither fix is implemented in the current tool — this is
named here as an open limitation, not silently patched over.