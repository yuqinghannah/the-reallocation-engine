"""
Component 3 — Bias Audit (data -> output)
ux-designer-sponsor-triage (Audited)

Run with: python bias_audit.py
"""

import csv
import re

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"

DESIGN_PATTERN = re.compile(
    r"designer|ux design|product design|interaction design|experience design",
    re.IGNORECASE
)

FUNDING_STAGE_SCORE = {
    "pre-seed": 1, "seed": 2, "series a": 3, "series b": 4,
    "series c": 5, "series d+": 6,
}

def is_blank(v):
    return v is None or v.strip() == ""

def age_bucket(age):
    if age is None:
        return "Unknown Age"
    if age < 3:
        return "Young (<3 yrs)"
    if age < 8:
        return "Mid (3-8 yrs)"
    return "Mature (8+ yrs)"

def funding_bucket(stage_raw):
    s = (stage_raw or "").strip().lower()
    if s in ("pre-seed", "seed"):
        return "Early (Pre-Seed/Seed)"
    if s in ("series a", "series b"):
        return "Growth (Series A/B)"
    if s in ("series c", "series d+"):
        return "Late (Series C/D+)"
    return "Unknown/Blank Stage"

def score_row(row):
    titles = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = row.get("latest_funding_stage", "") or ""

    if is_blank(titles) and is_blank(approvals_raw):
        tier = "Insufficient Data"
    else:
        design_match = bool(DESIGN_PATTERN.search(titles))
        try:
            approvals = float(approvals_raw)
        except ValueError:
            approvals = 0.0
        try:
            denials = float(denials_raw)
        except ValueError:
            denials = 0.0
        total_decisions = approvals + denials
        approval_rate = (approvals / total_decisions) if total_decisions > 0 else None
        stage_score = FUNDING_STAGE_SCORE.get(stage_raw.strip().lower(), 0)

        score = 0.0
        if design_match:
            score += 40.0
        if approval_rate is not None:
            score += approval_rate * 35.0
        score += (stage_score / 6.0) * 25.0

        if score >= 65:
            tier = "Top"
        elif score >= 35:
            tier = "Watch"
        else:
            tier = "Low Priority"

    return tier

def main():
    age_groups = {}
    funding_groups = {}

    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tier = score_row(row)
            usable = tier in ("Top", "Watch")

            age_raw = row.get("company_age_years", "")
            try:
                age = float(age_raw)
            except ValueError:
                age = None
            ab = age_bucket(age)
            age_groups.setdefault(ab, {"n": 0, "usable": 0})
            age_groups[ab]["n"] += 1
            if usable:
                age_groups[ab]["usable"] += 1

            fb = funding_bucket(row.get("latest_funding_stage", ""))
            funding_groups.setdefault(fb, {"n": 0, "usable": 0})
            funding_groups[fb]["n"] += 1
            if usable:
                funding_groups[fb]["usable"] += 1

    print("=== SELECTION RATE BY COMPANY AGE (usable signal = Top or Watch tier) ===")
    rates_age = {}
    for group, d in age_groups.items():
        rate = d["usable"] / d["n"] if d["n"] > 0 else 0
        rates_age[group] = rate
        print(f"{group:<20} n={d['n']:<8} usable={d['usable']:<6} rate={rate:.4f} ({rate*100:.2f}%)")
    max_rate = max(rates_age.values())
    min_rate = min(rates_age.values())
    print(f"Disparate impact ratio (min/max selection rate) across age groups: "
          f"{min_rate/max_rate:.3f}  [four-fifths rule threshold = 0.80]")
    print()

    print("=== SELECTION RATE BY FUNDING STAGE (usable signal = Top or Watch tier) ===")
    rates_funding = {}
    for group, d in funding_groups.items():
        rate = d["usable"] / d["n"] if d["n"] > 0 else 0
        rates_funding[group] = rate
        print(f"{group:<25} n={d['n']:<8} usable={d['usable']:<6} rate={rate:.4f} ({rate*100:.2f}%)")
    max_rate_f = max(rates_funding.values())
    min_rate_f = min(rates_funding.values())
    print(f"Disparate impact ratio (min/max selection rate) across funding groups: "
          f"{min_rate_f/max_rate_f:.3f}  [four-fifths rule threshold = 0.80]")

if __name__ == "__main__":
    main()