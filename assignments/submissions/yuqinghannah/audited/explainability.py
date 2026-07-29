"""
Component 4 — Explainability & Its Critique
ux-designer-sponsor-triage (Audited)

Part A: Counterfactual explanation for one sample company.
Part B: Audit of exactly which title strings the "designer" match
        actually caught, across Top + Watch tier companies — to check
        whether the explanation ("has design-title H-1B history") is
        technically true but practically misleading in any case.

Run with: python explainability.py
"""

import csv
import re
import ast

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

def parse_titles(raw):
    try:
        return ast.literal_eval(raw)
    except Exception:
        return []

def score_and_tier(titles, approvals_raw, denials_raw, stage_raw):
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
    stage_score = FUNDING_STAGE_SCORE.get((stage_raw or "").strip().lower(), 0)

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
    return score, tier, design_match, approval_rate, stage_score

def main():
    matched_titles_all = []
    watch_and_below_rows = []

    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles_raw = row.get("top_job_titles_sponsored", "") or ""
            if is_blank(titles_raw):
                continue
            score, tier, design_match, approval_rate, stage_score = score_and_tier(
                titles_raw,
                row.get("Total Approvals", ""),
                row.get("Total Denials", ""),
                row.get("latest_funding_stage", ""),
            )
            if tier in ("Top", "Watch") and design_match:
                title_list = parse_titles(titles_raw)
                for t in title_list:
                    if DESIGN_PATTERN.search(t):
                        matched_titles_all.append((row.get("company_name", ""), t))
            if tier == "Watch":
                watch_and_below_rows.append({
                    "company_name": row.get("company_name", ""),
                    "score": score,
                    "titles_raw": titles_raw,
                    "approval_rate": approval_rate,
                    "stage_score": stage_score,
                })

    print("=== PART A: COUNTERFACTUAL EXPLANATION (one sample Watch-tier company) ===")
    # pick a Watch company closest to the Top threshold (65) from below
    watch_and_below_rows.sort(key=lambda r: -r["score"])
    if watch_and_below_rows:
        sample = watch_and_below_rows[0]
        gap = 65 - sample["score"]
        print(f"Company: {sample['company_name']}")
        print(f"Current score: {sample['score']:.1f}  (Tier = Watch, threshold for Top = 65.0)")
        print(f"Gap to Top tier: {gap:.1f} points")
        print("Counterfactual: this company would cross into 'Top' tier if EITHER:")
        print(f"  - its approval rate rose enough to add {gap:.1f} more points "
              f"(approval_rate contributes up to 35 pts total), OR")
        print(f"  - its funding stage advanced enough to add {gap:.1f} more points "
              f"(funding stage contributes up to 25 pts total, in 1/6 steps of ~4.17 pts each)")
    print()

    print("=== PART B: TITLE-MATCH AUDIT (all distinct 'designer' matches in Top/Watch tiers) ===")
    unique_titles = sorted(set(t for _, t in matched_titles_all))
    print(f"Total distinct matched title strings: {len(unique_titles)}")
    for t in unique_titles:
        print(f"  - {t}")

if __name__ == "__main__":
    main()