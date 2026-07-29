# AI Use Disclosure — ux-designer-sponsor-triage (Audited)

**Tool(s) used:** Claude (Anthropic), used interactively throughout the
assignment via chat.

**Portions assisted:** Claude drafted all Python scripts (`gigo_eda.py`,
`score_companies.py`, `bias_audit.py`, `explainability.py`,
`causal_check.py`, `adversarial_test.py`, `funding_recency.py`,
`make_chart.py`), drafted the structure and first-pass text of all seven
validation report sections (GIGO_GATE.md, BIAS_AUDIT.md, EXPLAINABILITY.md,
CAUSAL_REASONING.md, ADVERSARIAL_ROBUSTNESS.md, DELEGATION_HARDSTOP.md,
WORKED_RUN.md), and walked me step-by-step through terminal/Git commands.

**How used:** I ran every script myself on my own machine against the real
CSV data and pasted the actual terminal output back into the conversation.
Claude then interpreted those real numbers and drafted the write-up
around them. I did not ask Claude to invent numbers — every score,
percentage, and company name in the reports comes from output I generated
and verified myself, including a real `npm run ats:liveness` check against
a live job posting I sourced myself (a Nagarro Junior Product Designer
listing) and the discovery that Playwright's browser binaries weren't
installed, which I fixed by running `npx playwright install`.

**What I changed:** I redirected the liveness test after the first
proposed URL (a LinkedIn "recommended jobs" page) turned out to be blocked
by LinkedIn's robots.txt — I found and substituted a real SmartRecruiters
job posting myself. I also chose the domain focus (Access/Eligibility —
H-1B sponsorship triage for design roles) and the specific fairness
groupings analyzed in the Bias Audit (company age and funding stage),
based on the failure modes I had already identified in my own Domain
Justification from a prior assignment on this same engine.

**What the AI could not do:** During the Adversarial Robustness test,
Claude's script correctly found every string in the dataset that matched
the regex pattern for "designer" — including "Motion Designer, Brand
Studio," "Industrial Designer," and "3D Designer." But the script had no
way to know, on its own, that these are professionally distinct
disciplines from Product/UX Designer — a string match is not a judgment
about occupational categories. That judgment came from me: as a
Product/UX design student, I recognized that a company that has only ever
sponsored an "Industrial Designer" (a hardware/physical-product
discipline) or a "Motion Designer" (a brand/motion-graphics discipline)
has demonstrated nothing about its willingness to sponsor a *digital
product* designer — these roles typically sit in different departments,
report to different hiring managers, and draw from entirely different
talent pools than the one I'm targeting. Claude could report *that* a
string matched; only my own professional domain knowledge could establish
*whether the match meant what a job-seeker would assume it meant*. That
distinction is the actual finding behind the Explainability critique and
the Adversarial Robustness section — the model surfaced the raw evidence,
but the interpretation of what that evidence does and doesn't prove about
occupational relevance required my own accountability and domain
expertise, not the model's.