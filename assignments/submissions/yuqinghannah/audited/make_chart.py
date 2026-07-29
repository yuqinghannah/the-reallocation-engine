"""
Uncertainty Visualization — ux-designer-sponsor-triage (Audited)
Stacked bar chart: tier x confidence level, so a viewer can see at a
glance that even "Top" tier companies vary in how much real evidence
backs their score.

Run with: python make_chart.py
(If matplotlib is missing, run: pip install matplotlib --break-system-packages)
"""

import csv
import re
import matplotlib.pyplot as plt

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
    stage_raw = row.get("latest_funding_stage", "") or ""

    if is_blank(titles) and is_blank(approvals_raw):
        return "Insufficient Data", "Low"

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

    return tier, confidence

def main():
    counts = {}
    tiers = ["Insufficient Data", "Low Priority", "Watch", "Top"]
    confidences = ["High", "Medium", "Low"]
    for t in tiers:
        counts[t] = {c: 0 for c in confidences}

    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tier, confidence = score_row(row)
            counts[tier][confidence] += 1

    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = [0] * len(tiers)
    colors = {"High": "#2E7D32", "Medium": "#F9A825", "Low": "#C62828"}

    for conf in confidences:
        values = [counts[t][conf] for t in tiers]
        ax.bar(tiers, values, bottom=bottom, label=f"Confidence: {conf}",
               color=colors[conf])
        bottom = [b + v for b, v in zip(bottom, values)]

    ax.set_yscale("log")
    ax.set_ylabel("Number of companies (log scale)")
    ax.set_title("ux-designer-sponsor-triage: Tier x Confidence Breakdown\n"
                  "(even 'Top' tier contains Medium-confidence companies)")
    ax.legend()
    plt.tight_layout()
    plt.savefig("tier_confidence_chart.png", dpi=150)
    print("Saved chart to tier_confidence_chart.png")
    print()
    for t in tiers:
        print(f"{t}: {counts[t]}")

if __name__ == "__main__":
    main()