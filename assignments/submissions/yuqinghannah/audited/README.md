# ux-designer-sponsor-triage — Audited Submission

This folder contains the full submission for **The Reallocation Engine,
Audited** (INFO 7375 — Computational Skepticism for AI).

## Main Report
**`Huang_Yuqing_ReallocationEngine.md`** — the consolidated validation
report. Read this first; it contains all 7 required components plus the
uncertainty visualization and AI Use Disclosure, assembled in order.

## How to Run the Tool

All commands assume you are in the repo root (`the-reallocation-engine/`)
and have run `npm install` per the repo's own setup instructions.

```powershell
# 1. Skeptical EDA / GIGO gate check
python assignments\submissions\yuqinghannah\audited\gigo_eda.py

# 2. Main scoring tool — produces the tiered reallocation recommendation
python assignments\submissions\yuqinghannah\audited\score_companies.py

# 3. Bias audit (selection rate by company age / funding stage)
python assignments\submissions\yuqinghannah\audited\bias_audit.py

# 4. Explainability — counterfactual explanation + title-match audit
python assignments\submissions\yuqinghannah\audited\explainability.py

# 5. Causal reasoning support check (approval rate vs. funding stage)
python assignments\submissions\yuqinghannah\audited\causal_check.py

# 6. Adversarial robustness test
python assignments\submissions\yuqinghannah\audited\adversarial_test.py

# 7. Funding recency check (hard-stop gate support)
python assignments\submissions\yuqinghannah\audited\funding_recency.py

# 8. Uncertainty visualization (requires matplotlib: pip install matplotlib --break-system-packages)
python assignments\submissions\yuqinghannah\audited\make_chart.py
```

All scripts read directly from `data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv`
(already present in the repo) and require no additional setup beyond Python 3
and `pip install matplotlib --break-system-packages` for the chart script.

For the real liveness check referenced in the Hard-Stop Gate section:
```powershell
npx playwright install   # one-time setup, downloads headless browser binaries
npm run ats:liveness -- "<job-posting-url>"
```

## File Index

| File | Component |
|---|---|
| `Huang_Yuqing_ReallocationEngine.md` | **Main consolidated report (read this)** |
| `GIGO_GATE.md` | Component 2 — Data validation |
| `BIAS_AUDIT.md` | Component 3 — Bias audit |
| `EXPLAINABILITY.md` | Component 4 — Explainability & critique |
| `CAUSAL_REASONING.md` | Component 5 — Pearl's three rungs |
| `ADVERSARIAL_ROBUSTNESS.md` | Component 6 — Adversarial robustness |
| `DELEGATION_HARDSTOP.md` | Component 7 — Delegation map + hard-stop gate |
| `WORKED_RUN.md` | Worked run + attestation |
| `FRICTIONAL_JOURNAL.md` | Required gate — prediction + reflection |
| `AI_USE_DISCLOSURE.md` | Required gate — AI use disclosure |
| `tier_confidence_chart.png` | Uncertainty visualization |
| `*.py` | All runnable scripts (see "How to Run" above) |