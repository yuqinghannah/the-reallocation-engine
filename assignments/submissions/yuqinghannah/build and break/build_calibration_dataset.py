"""
Step A for Calibration instrument.
Re-runs the SAME scoring logic as score_companies.py (unchanged — we are
calibrating the artifact AS BUILT, warts included), then attaches:
  - a numeric "claimed probability" derived from the tool's own stated
    confidence label (High=0.9, Medium=0.6, Low=0.3 — this mapping is an
    explicit, documented interpretation choice we are making in order to
    test the label numerically; the tool itself never states a number)
  - the real outcome label: does this company have an actual DOL H-1B
    decision on record? (Total Approvals + Total Denials > 0)
  - a flag for whether latest_funding_stage was blank (the distribution
    shift slice we will re-test calibration on)

Writes calibration_dataset.csv with one row per company (excluding the
"Insufficient Data" tier, which was already deliberately gated out of
scoring by the original tool and is not a probability claim at all).

Run with: python build_calibration_dataset.py
"""

import csv
import re

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"
OUT_PATH = "calibration_dataset.csv"

DESIGN_PATTERN = re.compile(
    r"designer|ux design|product design|interaction design|experience design",
    re.IGNORECASE
)

FUNDING_STAGE_SCORE = {
    "pre-seed": 1, "seed": 2, "series a": 3, "series b": 4,
    "series c": 5, "series d+": 6,
}

CLAIMED_PROB = {"High": 0.9, "Medium": 0.6, "Low": 0.3}

def is_blank(v):
    return v is None or v.strip() == ""

def score_row(row):
    """Unchanged from score_companies.py — the artifact as built."""
    titles = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = (row.get("latest_funding_stage", "") or "").strip().lower()

    if is_blank(titles) and is_blank(approvals_raw):
        return {"tier": "Insufficient Data", "confidence": "Low", "score": None}

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

    score = 0.0
    if design_match:
        score += 40.0
    if approval_rate is not None:
        score += approval_rate * 35.0
    score += (stage_score / 6.0) * 25.0

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

    return {
        "tier": tier,
        "confidence": confidence,
        "score": round(score, 1),
        "design_match": design_match,
        "total_decisions": total_decisions,
        "stage_raw": stage_raw,
    }

def main():
    out_rows = []
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = score_row(row)
            if r["tier"] == "Insufficient Data":
                continue  # already gated out by the tool itself, not a claim

            stage_field_original = row.get("latest_funding_stage", "") or ""
            blank_stage = is_blank(stage_field_original)

            approvals_raw = row.get("Total Approvals", "")
            denials_raw = row.get("Total Denials", "")
            try:
                approvals = float(approvals_raw)
            except ValueError:
                approvals = 0.0
            try:
                denials = float(denials_raw)
            except ValueError:
                denials = 0.0
            has_decision_record = 1 if (approvals + denials) > 0 else 0

            out_rows.append({
                "company_name": row.get("company_name", "").strip(),
                "confidence": r["confidence"],
                "claimed_prob": CLAIMED_PROB[r["confidence"]],
                "outcome_has_decision_record": has_decision_record,
                "blank_funding_stage": 1 if blank_stage else 0,
                "tier": r["tier"],
                "score": r["score"],
                "design_match": 1 if r["design_match"] else 0,
                "total_decisions": r["total_decisions"],
            })

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {OUT_PATH}")
    print(f"(excluded Insufficient Data rows, which are not probability claims)")

    # Quick sample-size sanity check per confidence bucket
    from collections import Counter
    conf_counts = Counter(r["confidence"] for r in out_rows)
    print("\n=== Sample size per stated confidence bucket ===")
    for conf in ["Low", "Medium", "High"]:
        print(f"{conf}: {conf_counts.get(conf, 0)} rows")

if __name__ == "__main__":
    main()
