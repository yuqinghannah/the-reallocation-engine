"""
Step B for Calibration instrument (Ch2 + Ch11).
Reads calibration_dataset.csv (from build_calibration_dataset.py) and:
  1. Plots the reliability diagram (claimed probability vs. actual outcome
     rate, against the diagonal) for the tool's stated confidence labels.
  2. Computes Brier score and ECE.
  3. Fits a single temperature parameter T on the logits of the claimed
     probabilities to minimize NLL against the real outcome, then re-plots.
  4. Re-runs everything on the "blank funding stage" slice only — the
     distribution-shift test tied to the Data-frame audit finding — using
     the SAME temperature fit on the full data, and reports what moved.

Requires matplotlib (already used elsewhere in this repo for
tier_confidence_chart.png). If missing: pip install matplotlib

Run with: python calibration_analysis.py
"""

import csv
import math
import matplotlib.pyplot as plt

IN_PATH = "calibration_dataset.csv"

def load_rows():
    rows = []
    with open(IN_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append({
                "confidence": r["confidence"],
                "claimed_prob": float(r["claimed_prob"]),
                "outcome": int(r["outcome_has_decision_record"]),
                "blank_stage": int(r["blank_funding_stage"]),
            })
    return rows

def bucket_stats(rows):
    """Group by stated confidence label, compute claimed vs actual rate."""
    buckets = {}
    for r in rows:
        b = buckets.setdefault(r["confidence"], {"n": 0, "claimed": r["claimed_prob"], "actual_sum": 0})
        b["n"] += 1
        b["actual_sum"] += r["outcome"]
    for conf, b in buckets.items():
        b["actual_rate"] = b["actual_sum"] / b["n"] if b["n"] > 0 else float("nan")
    return buckets

def brier_score(rows, prob_key="claimed_prob"):
    return sum((r[prob_key] - r["outcome"]) ** 2 for r in rows) / len(rows)

def ece(buckets, total_n):
    """Expected Calibration Error, weighted by bucket size."""
    total = 0.0
    for conf, b in buckets.items():
        weight = b["n"] / total_n
        total += weight * abs(b["claimed"] - b["actual_rate"])
    return total

def logit(p, eps=1e-6):
    p = min(max(p, eps), 1 - eps)
    return math.log(p / (1 - p))

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def nll_for_temperature(rows, T):
    total = 0.0
    for r in rows:
        z = logit(r["claimed_prob"]) / T
        p = sigmoid(z)
        p = min(max(p, 1e-6), 1 - 1e-6)
        y = r["outcome"]
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(rows)

def fit_temperature(rows):
    """Simple grid search — no external optimizer needed."""
    best_T, best_nll = 1.0, float("inf")
    T = 0.05
    while T <= 10.0:
        nll = nll_for_temperature(rows, T)
        if nll < best_nll:
            best_nll, best_T = nll, T
        T += 0.05
    return best_T, best_nll

def apply_temperature(rows, T):
    for r in rows:
        z = logit(r["claimed_prob"]) / T
        r["calibrated_prob"] = sigmoid(z)
    return rows

def bucket_stats_calibrated(rows):
    buckets = {}
    for r in rows:
        b = buckets.setdefault(r["confidence"], {"n": 0, "claimed_sum": 0, "actual_sum": 0})
        b["n"] += 1
        b["claimed_sum"] += r["calibrated_prob"]
        b["actual_sum"] += r["outcome"]
    for conf, b in buckets.items():
        b["claimed_avg"] = b["claimed_sum"] / b["n"]
        b["actual_rate"] = b["actual_sum"] / b["n"]
    return buckets

def plot_reliability(buckets, title, out_path, claimed_key="claimed"):
    order = ["Low", "Medium", "High"]
    xs = [buckets[c][claimed_key] for c in order if c in buckets]
    ys = [buckets[c]["actual_rate"] for c in order if c in buckets]
    ns = [buckets[c]["n"] for c in order if c in buckets]
    labels = [c for c in order if c in buckets]

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot([0, 1], [0, 1], linestyle="--", color="gray", label="Perfect calibration")
    ax.scatter(xs, ys, s=[max(n, 20) for n in ns], color="crimson", zorder=3)
    for x, y, label, n in zip(xs, ys, labels, ns):
        ax.annotate(f"{label}\n(n={n})", (x, y), textcoords="offset points", xytext=(8, 5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Claimed probability (from stated confidence label)")
    ax.set_ylabel("Actual rate of having a real DOL decision on record")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")

def main():
    rows = load_rows()
    total_n = len(rows)
    print(f"=== Loaded {total_n} rows ===\n")

    # --- BEFORE calibration: use the tool's raw claimed probabilities ---
    buckets_before = bucket_stats(rows)
    print("=== BEFORE temperature scaling: claimed vs actual, by stated confidence ===")
    for conf in ["Low", "Medium", "High"]:
        if conf in buckets_before:
            b = buckets_before[conf]
            print(f"{conf:<8} n={b['n']:<8} claimed={b['claimed']:.2f}  actual={b['actual_rate']:.4f}")
    brier_before = brier_score(rows)
    ece_before = ece(buckets_before, total_n)
    print(f"\nBrier score (before): {brier_before:.4f}")
    print(f"ECE (before): {ece_before:.4f}\n")
    plot_reliability(buckets_before, "Reliability diagram — BEFORE temperature scaling",
                      "reliability_before.png")

    # --- Fit temperature on FULL dataset ---
    best_T, best_nll = fit_temperature(rows)
    print(f"\n=== Fitted temperature T = {best_T:.2f} (NLL={best_nll:.4f}) ===\n")
    rows = apply_temperature(rows, best_T)

    buckets_after = bucket_stats_calibrated(rows)
    print("=== AFTER temperature scaling: claimed(avg) vs actual, by stated confidence ===")
    for conf in ["Low", "Medium", "High"]:
        if conf in buckets_after:
            b = buckets_after[conf]
            print(f"{conf:<8} n={b['n']:<8} claimed_avg={b['claimed_avg']:.4f}  actual={b['actual_rate']:.4f}")
    brier_after = sum((r["calibrated_prob"] - r["outcome"]) ** 2 for r in rows) / total_n
    ece_after = 0.0
    for conf, b in buckets_after.items():
        ece_after += (b["n"] / total_n) * abs(b["claimed_avg"] - b["actual_rate"])
    print(f"\nBrier score (after): {brier_after:.4f}")
    print(f"ECE (after): {ece_after:.4f}\n")
    plot_reliability(
        {c: {"claimed_avg": b["claimed_avg"], "actual_rate": b["actual_rate"], "n": b["n"]}
         for c, b in buckets_after.items()},
        "Reliability diagram — AFTER temperature scaling",
        "reliability_after.png",
        claimed_key="claimed_avg",
    )

    # --- DISTRIBUTION SHIFT SLICE: blank funding stage rows only ---
    print("\n" + "=" * 70)
    print("DISTRIBUTION SHIFT TEST: blank-funding-stage slice")
    print("(using the SAME temperature T fit on the full data above)")
    print("=" * 70 + "\n")
    shift_rows = [r for r in rows if r["blank_stage"] == 1]
    print(f"Rows in blank-funding-stage slice: {len(shift_rows)} "
          f"({len(shift_rows)/total_n*100:.1f}% of scored rows)\n")

    if len(shift_rows) == 0:
        print("No blank-stage rows found in scored set — cannot run shift test.")
        return

    buckets_shift = bucket_stats_calibrated(shift_rows)
    print("=== Blank-stage slice: claimed(avg, using full-data T) vs actual ===")
    for conf in ["Low", "Medium", "High"]:
        if conf in buckets_shift:
            b = buckets_shift[conf]
            print(f"{conf:<8} n={b['n']:<8} claimed_avg={b['claimed_avg']:.4f}  actual={b['actual_rate']:.4f}")

    brier_shift = sum((r["calibrated_prob"] - r["outcome"]) ** 2 for r in shift_rows) / len(shift_rows)
    ece_shift = 0.0
    for conf, b in buckets_shift.items():
        ece_shift += (b["n"] / len(shift_rows)) * abs(b["claimed_avg"] - b["actual_rate"])
    print(f"\nBrier score (blank-stage slice): {brier_shift:.4f}  "
          f"[full-data after-calibration Brier was {brier_after:.4f}]")
    print(f"ECE (blank-stage slice): {ece_shift:.4f}  "
          f"[full-data after-calibration ECE was {ece_after:.4f}]")

    plot_reliability(
        {c: {"claimed_avg": b["claimed_avg"], "actual_rate": b["actual_rate"], "n": b["n"]}
         for c, b in buckets_shift.items()},
        "Reliability diagram — blank-funding-stage slice (distribution shift)",
        "reliability_shift_blank_stage.png",
        claimed_key="claimed_avg",
    )

if __name__ == "__main__":
    main()
