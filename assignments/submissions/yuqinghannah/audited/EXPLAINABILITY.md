# Explainability & Its Critique — ux-designer-sponsor-triage

## Part A: Counterfactual Explanation

Because the scoring formula is a transparent additive rule (not a black-box
model), the most honest explanation method here is a **counterfactual**:
for any company, we can state exactly what would need to change for its
tier to flip.

**Sample company:** `1LIFE HEALTHCARE INC`
- Current score: **60.0** (Tier = Watch; threshold for Top = 65.0)
- Gap to Top tier: **5.0 points**

**Counterfactual:** this company would cross into "Top" tier if EITHER:
- its approval rate rose enough to add 5.0 more points (approval rate
  contributes up to 35 points total, so roughly a 14-percentage-point
  increase in approval rate would close the gap), **or**
- its funding stage advanced one step (funding stage contributes up to 25
  points total in 1/6 increments of ~4.17 points each — so two stage
  increases, e.g. Series A → Series C, would close the gap on its own).

This is a real, checkable explanation: every point in the score traces to
a specific field in the source CSV, and the counterfactual states an exact
condition, not a vague "it would need to be a stronger company."

## Part B: Title-Match Audit — Where the Explanation Becomes Misleading

Running the audit against every company currently in the Top or Watch tier
turned up **44 distinct job-title strings** that the tool counted as
"design-title H-1B history" (the 40-point "design match" component of the
score). Most are legitimately Product/UX/Interaction Designer roles
("Senior UX Designer," "Founding Product Designer," "Lead Product
Designer"). But several are not:

```
- 3D Designer
- Architectural Designer II
- Industrial Designer
- Motion Designer, Brand Studio
- Senior Designer, Motion Graphics
```

**The misleading case:** For any company whose *only* matched title is one
of these, the tool's explanation reads: *"has design-title H-1B history"* —
which is **technically true** (the string literally matched the regex) but
**practically misleading**, because 3D design, architectural design,
industrial design, and motion/brand design are different professional
disciplines from Product/UX Designer. A company that has only ever
sponsored an "Industrial Designer" role has demonstrated nothing about its
willingness to sponsor a *digital product* designer — the two roles
involve different hiring managers, different budgets, and often entirely
different departments (industrial design often sits in hardware/physical
product teams, not the software product org this tool's user is targeting).

**Why this gap is the point, not a plot problem:** the explanation is not
lying about *what matched* — it is silent about *whether the match means
what the user will assume it means.* A job-seeker reading "has design-title
H-1B history" would reasonably assume it means their specific discipline.
The explanation format currently has no way to signal "matched, but on an
adjacent discipline" versus "matched, and it's the real thing." This is
exactly the title-string-blindness failure mode named in the original
Domain Justification, now confirmed with real matched title strings from
the tool's actual Top/Watch tier output — not a hypothetical concern.

**What this means for trust:** any company whose Top/Watch placement rests
*only* on one of these adjacent-discipline titles should be treated with
lower confidence than the explanation field currently communicates. The
tool's `confidence` field (High/Medium/Low) is based on *approval count*,
not on *discipline match quality* — so a company could show `confidence:
High` while its only "design match" is an Industrial Designer title. This
is a real limitation the current confidence field does not catch, and is
carried forward into the Adversarial Robustness component.