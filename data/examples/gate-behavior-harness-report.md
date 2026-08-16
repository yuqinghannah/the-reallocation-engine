# Role Scorer report — 2026-08-16

*Bayesian Role Scorer (Ch.11). Weights: sponsorship 0.35, fit 0.3, role_quality 0 [role_quality weight is **[VERIFY]** — not pinned by the chapter]. Threshold 0.3. Profile requires sponsorship.*

**Summary:** 4 roles → Apply 1 · Consider 0 · Skip 3. **Skip rate 75%** (healthy — a good run skips at least half).

| Role | Composite | Rec | Why | Audit (term · value · weight · source) |
|---|---|---|---|---|
| SYNTHETIC-TEST-CO-A — [harness] control case — all gates open | 0.570 | **Apply** | composite 0.570 ≥ 0.3, gates healthy | sponsorship 0.9·0.35 [record]; fit 0.85·0.3 [model-judgment] × liveness 1[record]×timeline 1[your-input]×funding_recency 1[record] |
| SYNTHETIC-TEST-CO-D — [harness] funding_recency gate closed, all else high | 0.029 | **Skip** | gated: funding_recency ≈ 0.050 (a closed gate zeroes the composite regardless of votes) | sponsorship 0.9·0.35 [record]; fit 0.85·0.3 [model-judgment] × liveness 1[record]×timeline 1[your-input]×funding_recency 0.05[record] |
| SYNTHETIC-TEST-CO-B — [harness] liveness gate closed, all else high | 0.000 | **Skip** | gated: liveness ≈ 0.000 (a closed gate zeroes the composite regardless of votes) | sponsorship 0.9·0.35 [record]; fit 0.85·0.3 [model-judgment] × liveness 0[record]×timeline 1[your-input]×funding_recency 1[record] |
| SYNTHETIC-TEST-CO-C — [harness] timeline gate closed, all else high | 0.000 | **Skip** | gated: timeline ≈ 0.000 (a closed gate zeroes the composite regardless of votes) | sponsorship 0.9·0.35 [record]; fit 0.85·0.3 [model-judgment] × liveness 1[record]×timeline 0[your-input]×funding_recency 1[record] |

*Every term traces to its source. If you cannot explain a row term-by-term, distrust the recommendation before your confusion (Ch.11).*
