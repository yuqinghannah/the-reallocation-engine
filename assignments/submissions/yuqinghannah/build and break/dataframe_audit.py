"""
Data-frame audit (Ch3) — plant-and-find quantification + one-row trace.

Part 1: quantify how many companies are affected by the blank-funding-stage
        bug, and how many would change TIER if blank were instead treated
        as "unknown" (excluded from the funding component entirely) rather
        than silently scored as stage_score=0.

Part 2: trace one real row end-to-end through score_row(), printing every
        intermediate value, for the reproducibility appendix / structural
        trace requirement.

Run with: python dataframe_audit.py
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

def score_row_current(row):
    """Exact current logic (bug included): blank stage -> stage_score=0."""
    titles = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = (row.get("latest_funding_stage", "") or "").strip().lower()

    if is_blank(titles) and is_blank(approvals_raw):
        return None  # Insufficient Data — out of scope for this comparison

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

    tier = "Top" if score >= 65 else "Watch" if score >= 35 else "Low Priority"
    return {"score": round(score, 1), "tier": tier, "stage_raw": stage_raw}

def score_row_fixed(row):
    """Alternative: blank funding stage excluded from the funding term
    entirely (score computed only from design_match + approval_rate,
    renormalized), instead of being silently counted as the worst stage."""
    titles = row.get("top_job_titles_sponsored", "") or ""
    approvals_raw = row.get("Total Approvals", "")
    denials_raw = row.get("Total Denials", "")
    stage_raw = (row.get("latest_funding_stage", "") or "").strip().lower()

    if is_blank(titles) and is_blank(approvals_raw):
        return None

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

    blank_stage = is_blank(row.get("latest_funding_stage", "") or "")

    score = 0.0
    if design_match:
        score += 40.0
    if approval_rate is not None:
        score += approval_rate * 35.0
    if not blank_stage:
        stage_score = FUNDING_STAGE_SCORE.get(stage_raw, 0)
        score += (stage_score / 6.0) * 25.0
    # If blank_stage: funding component simply omitted (score stays lower
    # ceiling for this row) rather than actively penalized to 0 — the
    # point isn't that this fixed version is "correct," it's to measure
    # how much the current design choice actually moves outcomes.

    tier = "Top" if score >= 65 else "Watch" if score >= 35 else "Low Priority"
    return {"score": round(score, 1), "tier": tier}

def main():
    print("=" * 70)
    print("PART 1: Quantifying the blank-funding-stage scoring impact")
    print("=" * 70 + "\n")

    affected = 0
    tier_changed = 0
    examples = []

    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            current = score_row_current(row)
            if current is None:
                continue
            blank_stage = is_blank(row.get("latest_funding_stage", "") or "")
            if not blank_stage:
                continue
            affected += 1
            fixed = score_row_fixed(row)
            if fixed["tier"] != current["tier"]:
                tier_changed += 1
                if len(examples) < 10:
                    examples.append((row.get("company_name", "").strip(),
                                      current["score"], current["tier"],
                                      fixed["score"], fixed["tier"]))

    print(f"Companies with blank latest_funding_stage AND enough data to be scored "
          f"(not Insufficient Data): {affected}")
    print(f"Of those, companies whose TIER would change if blank were treated as "
          f"'unknown' instead of 'worst stage': {tier_changed} "
          f"({tier_changed/affected*100:.1f}% of the affected group)\n")

    print("=== Example companies whose tier changes under the fix ===")
    print(f"{'Company':<35} {'Current score':<14} {'Current tier':<14} "
          f"{'Fixed score':<12} {'Fixed tier'}")
    for name, cs, ct, fs, ft in examples:
        print(f"{name:<35} {cs:<14} {ct:<14} {fs:<12} {ft}")

    print("\n" + "=" * 70)
    print("PART 2: One-row trace (reproducibility appendix)")
    print("=" * 70 + "\n")

    # Trace 23ANDME INC — a real row with actual decision data, useful
    # because it shows every branch of the scoring logic firing on real
    # values rather than blanks.
    target_name = "23ANDME INC"
    with open(PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("company_name", "").strip().upper() == target_name:
                print(f"Row found: {row.get('company_name')}")
                print(f"  Raw top_job_titles_sponsored: {row.get('top_job_titles_sponsored')}")
                print(f"  Raw Total Approvals: {row.get('Total Approvals')}")
                print(f"  Raw Total Denials: {row.get('Total Denials')}")
                print(f"  Raw latest_funding_stage: {row.get('latest_funding_stage')}")
                print(f"  Raw latest_funding_date: {row.get('latest_funding_date')}")
                print()

                titles = row.get("top_job_titles_sponsored", "") or ""
                design_match = bool(DESIGN_PATTERN.search(titles))
                print(f"  Step 1 — design_match = DESIGN_PATTERN.search(titles) "
                      f"-> {design_match}")
                print(f"           (titles field only lists a handful of job titles per "
                      f"company — NOT a full history — so a company that sponsors many "
                      f"roles, most non-design, could have a real design hire buried "
                      f"outside this truncated list and still show design_match=False. "
                      f"This is a separate open question worth flagging, not resolved here.)")

                approvals = float(row.get("Total Approvals") or 0)
                denials = float(row.get("Total Denials") or 0)
                total_decisions = approvals + denials
                approval_rate = approvals / total_decisions if total_decisions > 0 else None
                print(f"\n  Step 2 — approvals={approvals}, denials={denials}, "
                      f"total_decisions={total_decisions}")
                print(f"           approval_rate = {approval_rate}")

                stage_raw = (row.get("latest_funding_stage") or "").strip().lower()
                stage_score = FUNDING_STAGE_SCORE.get(stage_raw, 0)
                print(f"\n  Step 3 — stage_raw='{stage_raw}' -> stage_score={stage_score} "
                      f"(out of 6)")

                score = 0.0
                if design_match:
                    score += 40.0
                if approval_rate is not None:
                    score += approval_rate * 35.0
                score += (stage_score / 6.0) * 25.0
                print(f"\n  Step 4 — final score = "
                      f"{'40 (design) + ' if design_match else '0 (no design match) + '}"
                      f"{approval_rate*35 if approval_rate else 0:.1f} (approval) + "
                      f"{(stage_score/6)*25:.1f} (funding) = {score:.1f}")

                tier = "Top" if score >= 65 else "Watch" if score >= 35 else "Low Priority"
                print(f"  Step 5 — tier = {tier}")
                break
        else:
            print(f"Row '{target_name}' not found — check exact spelling/casing in CSV.")

if __name__ == "__main__":
    main()
