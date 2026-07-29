"""
Quick check for Causal Reasoning (Rung 1 evidence):
Does approval rate correlate with funding stage among companies
that have any H-1B decision history at all?

Run with: python causal_check.py
"""

import csv

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"

def main():
    stage_data = {}
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                approvals = float(row.get("Total Approvals", "") or 0)
                denials = float(row.get("Total Denials", "") or 0)
            except ValueError:
                continue
            total = approvals + denials
            if total <= 0:
                continue
            stage = (row.get("latest_funding_stage", "") or "").strip().lower()
            if not stage:
                continue
            stage_data.setdefault(stage, {"n": 0, "sum_rate": 0.0, "sum_approvals": 0.0})
            rate = approvals / total
            stage_data[stage]["n"] += 1
            stage_data[stage]["sum_rate"] += rate
            stage_data[stage]["sum_approvals"] += approvals

    print("=== APPROVAL RATE AND VOLUME BY FUNDING STAGE (companies with any decisions) ===")
    order = ["pre-seed", "seed", "series a", "series b", "series c", "series d+"]
    for stage in order:
        d = stage_data.get(stage)
        if not d or d["n"] == 0:
            continue
        avg_rate = d["sum_rate"] / d["n"]
        avg_approvals = d["sum_approvals"] / d["n"]
        print(f"{stage:<12} n={d['n']:<6} avg_approval_rate={avg_rate:.1%}  "
              f"avg_total_approvals_per_company={avg_approvals:.1f}")

if __name__ == "__main__":
    main()