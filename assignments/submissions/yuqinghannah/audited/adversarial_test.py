"""
Component 6 — Adversarial Robustness & Fragility
ux-designer-sponsor-triage (Audited)

Perturbation being tested: a company whose ONLY matched "design" title is
from an adjacent-but-different discipline (Industrial Designer, 3D
Designer, Motion Designer, Architectural Designer) rather than a genuine
Product/UX Designer role. Does the tool still place it in a usable
(Top/Watch) tier as if it were real design-sponsorship evidence?

Run with: python adversarial_test.py
"""

import csv
import re
import ast

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"

DESIGN_PATTERN = re.compile(
    r"designer|ux design|product design|interaction design|experience design",
    re.IGNORECASE
)

# Titles confirmed (via Explainability audit) to be adjacent disciplines,
# NOT Product/UX Designer roles, despite matching the regex.
ADJACENT_DISCIPLINE_TITLES = {
    "3d designer", "architectural designer ii", "industrial designer",
    "motion designer, brand studio", "senior designer, motion graphics",
}

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

def score_row(row):
    titles_raw = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = row.get("latest_funding_stage", "") or ""

    if is_blank(titles_raw) and is_blank(approvals_raw):
        return None

    design_match = bool(DESIGN_PATTERN.search(titles_raw))
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

    return {
        "company_name": row.get("company_name", "").strip(),
        "score": round(score, 1),
        "tier": tier,
        "matched_titles": [t for t in parse_titles(titles_raw) if DESIGN_PATTERN.search(t)],
    }

def main():
    vulnerable_cases = []
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            result = score_row(row)
            if result is None or result["tier"] not in ("Top", "Watch"):
                continue
            matched_lower = [t.strip().lower() for t in result["matched_titles"]]
            # Vulnerable case: EVERY matched title is an adjacent-discipline title
            # (i.e., there is NO genuine Product/UX Designer title backing this company)
            if matched_lower and all(t in ADJACENT_DISCIPLINE_TITLES for t in matched_lower):
                vulnerable_cases.append(result)

    print("=== ADVERSARIAL TEST: companies in Top/Watch backed ONLY by ===")
    print("=== adjacent-discipline 'design' titles (not real Product/UX Designer) ===")
    print(f"Found {len(vulnerable_cases)} vulnerable case(s).")
    for c in vulnerable_cases:
        print(f"{c['company_name']:<35} tier={c['tier']:<6} score={c['score']:<6} "
              f"matched_titles={c['matched_titles']}")

if __name__ == "__main__":
    main()