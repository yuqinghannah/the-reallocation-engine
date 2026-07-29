"""
Component 7 support — Funding Recency Check (for the Hard-Stop Gate)
ux-designer-sponsor-triage (Audited)

Checks how old each Top-tier company's most recent funding round is,
relative to today's real date. A stale funding round is a signal that
the company's hiring/sponsorship budget may no longer reflect the
historical record the score is based on.

Run with: python funding_recency.py
"""

import csv
import re
from datetime import datetime

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"
TODAY = datetime(2026, 7, 29)  # real run date, stated explicitly (no snapshot-date field exists)
STALE_THRESHOLD_YEARS = 2.0

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

def main():
    top_companies = []
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            titles = row.get("top_job_titles_sponsored", "") or ""
            approvals_raw = row.get("Total Approvals", "")
            denials_raw = row.get("Total Denials", "")
            stage_raw = row.get("latest_funding_stage", "") or ""

            if is_blank(titles) and is_blank(approvals_raw):
                continue

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

            if score < 65:
                continue  # only checking Top tier

            date_str = row.get("latest_funding_date", "")
            years_since = None
            if not is_blank(date_str):
                try:
                    funding_date = datetime.strptime(date_str.strip(), "%Y-%m-%d")
                    years_since = (TODAY - funding_date).days / 365.25
                except ValueError:
                    years_since = None

            top_companies.append({
                "company_name": row.get("company_name", "").strip(),
                "score": round(score, 1),
                "latest_funding_date": date_str,
                "years_since_funding": years_since,
            })

    stale = [c for c in top_companies if c["years_since_funding"] is not None
             and c["years_since_funding"] > STALE_THRESHOLD_YEARS]
    fresh = [c for c in top_companies if c["years_since_funding"] is not None
             and c["years_since_funding"] <= STALE_THRESHOLD_YEARS]
    unknown = [c for c in top_companies if c["years_since_funding"] is None]

    print(f"=== FUNDING RECENCY CHECK (Top tier, {len(top_companies)} companies, "
          f"threshold={STALE_THRESHOLD_YEARS} years, reference date={TODAY.date()}) ===")
    print(f"Fresh (<= {STALE_THRESHOLD_YEARS} yrs since last round): {len(fresh)}")
    print(f"STALE (> {STALE_THRESHOLD_YEARS} yrs since last round):  {len(stale)}")
    print(f"Unknown/unparseable date: {len(unknown)}")
    print()
    print("=== Sample of STALE Top-tier companies (funding may no longer reflect current hiring budget) ===")
    for c in sorted(stale, key=lambda x: -x["years_since_funding"])[:10]:
        print(f"{c['company_name']:<35} score={c['score']:<6} "
              f"last_funding={c['latest_funding_date']:<12} "
              f"years_since={c['years_since_funding']:.1f}")

if __name__ == "__main__":
    main()