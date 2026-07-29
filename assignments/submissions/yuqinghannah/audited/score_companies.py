"""
Component 1 — The Working Reallocation Tool
ux-designer-sponsor-triage (Audited)

Objective (one plain sentence): Rank companies by estimated likelihood of
sponsoring a Product/UX Designer H-1B, using historical design-title
sponsorship approval rate, funding health, and company age, so a design
job-seeker can reallocate limited application time toward companies most
likely to sponsor.

What this objective leaves out: whether the company is actively hiring for
a sponsored role RIGHT NOW, whether it has budget for immigration
sponsorship this specific year, and whether the applicant's own
qualifications match the role. Past sponsorship of a title is not a
guarantee for a specific future hire.

Run with: python score_companies.py
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

def score_row(row):
    titles = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = (row.get("latest_funding_stage", "") or "").strip().lower()
    age_raw = row.get("company_age_years", "")

    # --- GIGO gate: no sponsorship signal at all -> separate tier, not scored down ---
    if is_blank(titles) and is_blank(approvals_raw):
        return {
            "tier": "Insufficient Data",
            "confidence": "Low",
            "score": None,
            "reason": "No H-1B sponsorship history of any kind on file for "
                      "this company. This does NOT mean the company refuses "
                      "to sponsor — it most likely means the company has "
                      "never filed any H-1B petition in the source data, "
                      "for any role.",
        }

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

    stage_score = FUNDING_STAGE_SCORE.get(stage_raw, 0)

    try:
        age = float(age_raw)
    except ValueError:
        age = None

    # --- composite score (0-100), each part explicit so it can be audited ---
    score = 0.0
    if design_match:
        score += 40.0
    if approval_rate is not None:
        score += approval_rate * 35.0
    score += (stage_score / 6.0) * 25.0

    # --- confidence: based on how much real evidence backs the score ---
    if design_match and total_decisions >= 3:
        confidence = "High"
    elif design_match or total_decisions >= 1:
        confidence = "Medium"
    else:
        confidence = "Low"

    if score >= 65:
        tier = "Top"
    elif score >= 35:
        tier = "Watch"
    else:
        tier = "Low Priority"

    reason_parts = []
    if design_match:
        reason_parts.append("has design-title H-1B history")
    if approval_rate is not None:
        reason_parts.append(f"approval rate {approval_rate:.0%}")
    if stage_raw:
        reason_parts.append(f"funding stage {stage_raw}")
    reason = "; ".join(reason_parts) if reason_parts else "limited signal"

    return {
        "tier": tier,
        "confidence": confidence,
        "score": round(score, 1),
        "reason": reason,
    }

def main():
    results = []
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = score_row(row)
            r["company_name"] = row.get("company_name", "").strip()
            results.append(r)

    tiers_count = {}
    for r in results:
        tiers_count[r["tier"]] = tiers_count.get(r["tier"], 0) + 1

    print("=== TIER DISTRIBUTION (all 30,369 companies) ===")
    for tier, count in sorted(tiers_count.items(), key=lambda x: -x[1]):
        print(f"{tier}: {count} ({count/len(results)*100:.1f}%)")
    print()

    print("=== SAMPLE: TOP 10 SCORED COMPANIES (Tier = Top) ===")
    top_companies = [r for r in results if r["tier"] == "Top"]
    top_companies.sort(key=lambda x: x["score"], reverse=True)
    for r in top_companies[:10]:
        print(f"{r['company_name']:<35} score={r['score']:<6} "
              f"confidence={r['confidence']:<7} reason={r['reason']}")
    print()

    print("=== SAMPLE: 5 'Insufficient Data' companies (should NOT be read as 'no') ===")
    insufficient = [r for r in results if r["tier"] == "Insufficient Data"]
    for r in insufficient[:5]:
        print(f"{r['company_name']:<35} tier={r['tier']} confidence={r['confidence']}")
# --- Break attempt: check for "Top" tier companies backed by thin evidence ---
    print()
    print("=== BREAK ATTEMPT: Top-tier companies with confidence != High ===")
    thin_evidence = [r for r in top_companies if r["confidence"] != "High"]
    print(f"Found {len(thin_evidence)} of {len(top_companies)} Top-tier companies "
          f"with confidence below High.")
    for r in thin_evidence[:10]:
        print(f"{r['company_name']:<35} score={r['score']:<6} "
              f"confidence={r['confidence']:<7} reason={r['reason']}")
# --- Concrete reallocation recommendation ---
    print()
    print("=== REALLOCATION RECOMMENDATION ===")
    watch_count = tiers_count.get("Watch", 0)
    print(f"Baseline (no tool): spend application-time equally across all "
          f"{len(top_companies)+watch_count} companies with any data.")
    print(f"Recommended reallocation: move effort so that ~70% of "
          f"application-writing time goes to the {len(top_companies)} "
          f"'Top' companies, ~25% to the {watch_count} 'Watch' companies, "
          f"~5% held as exploratory outreach to well-funded "
          f"'Insufficient Data' companies (since absence of history there "
          f"is not evidence of unwillingness).")
    print(f"Uncertainty flag: {len(thin_evidence)} of the {len(top_companies)} "
          f"'Top' recommendations rest on thin evidence (confidence=Medium, "
          f"not High) — treat these as lower-confidence within the Top tier, "
          f"not equal to the confidence=High ones.")
if __name__ == "__main__":
    main()