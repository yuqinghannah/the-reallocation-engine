# Delegation Map + The Hard-Stop Gate — ux-designer-sponsor-triage

## Delegation Map

| Component | Tool decides | Human decides | Override point |
|---|---|---|---|
| Data ingestion & GIGO gate | Whether a record passes/fails the quality gate | Whether to trust a borderline record | Human can override a "fail" if they have outside knowledge of the company |
| Scoring (Top/Watch/Insufficient Data/Low Priority) | The numeric score and tier, from verified fields only | Which tier's companies to actually apply to, and how much effort to spend | Human always makes the final application decision — the tool never applies on the user's behalf |
| Title-match ("has design-title H-1B history") | Whether a string matched the design-title pattern | Whether the matched title is *actually* the same discipline (Product/UX vs. Industrial/Motion/3D design) | **Mandatory human review** — the Adversarial Robustness test proved this cannot be trusted automatically |
| Funding health | Funding stage + date, as recorded | Whether the funding record is recent enough to represent current hiring reality | **Mandatory human review** — see Hard Stop #2 below |
| Posting liveness | Automated "live / dead / uncertain" check via headless browser | Final call on ambiguous ("uncertain") results | **Mandatory human review** — see Hard Stop #1 below |
| Time/effort reallocation | Recommends a % split (70/25/5) across tiers | The person's actual calendar and hours | The recommendation is advisory; the person decides how literally to follow it |

## Hard Stop #1 — Posting Liveness (implemented, real test run)

**Rule:** before a person spends any application-writing time on a specific
posting, the posting's liveness must be checked. The tool never assumes a
posting found via `top_job_titles_sponsored` history is currently open —
sponsorship history is about the *company*, not about whether a specific
role is live today.

**Real run:**
```
npm run ats:liveness -- "https://jobs.smartrecruiters.com/Nagarro1/744000136255459?trid=2d92f286-613b-4daf-9dfa-6340ffbecf73"

Checking 1 URL(s)...
⚠️ uncertain  https://jobs.smartrecruiters.com/Nagarro1/744000136255459?trid=...
           content present but no visible apply control found
Results: 0 active  0 expired  1 uncertain
```

**Response:** `uncertain` → **flag for human review**, never auto-approve
and never auto-reject. This is the gate working exactly as intended: rather
than guessing "probably still open" or "probably closed," the tool
surfaces its own uncertainty and stops. The person must manually open the
link and confirm before spending time on an application. This required a
real environment fix during testing — Playwright's browser binaries were
not yet installed (`npx playwright install`) — documented here as a real
setup step, not glossed over.

## Hard Stop #2 — Funding Recency (real finding, currently NOT implemented as a fix — flagged instead)

**Rule proposed:** a company's funding-stage score should not be trusted at
face value if its most recent funding round is more than 2 years old,
because a stale funding record likely no longer reflects current hiring
budget or headcount.

**Real check run against the actual 71 "Top" tier companies:**
```
=== FUNDING RECENCY CHECK (Top tier, 71 companies, threshold=2.0 years, reference date=2026-07-29) ===
Fresh (<= 2.0 yrs since last round): 7
STALE (> 2.0 yrs since last round):  64
Unknown/unparseable date: 0

=== Sample of STALE Top-tier companies ===
VIA TRANSPORATION INC     score=87.5  last_funding=2014-03-13  years_since=12.4
PAGE SOUTHERLAND PAGE INC score=77.8  last_funding=2014-04-01  years_since=12.3
YEXT INC                  score=95.8  last_funding=2014-05-28  years_since=12.2
SONOS INC                 score=98.9  last_funding=2014-11-18  years_since=11.7
MOXTRA INC                score=87.5  last_funding=2015-01-14  years_since=11.5
```

**This is a serious, real finding, not a minor edge case: 90% (64 of 71)
of the tool's highest-confidence "Top" tier recommendations rest on
funding data that is over 2 years old — several over a decade old.** This
directly validates a gap named by TA feedback on a prior assignment for
this same engine: a funding-recency check was proposed in this recipe's
original Phase Gates but never implemented until this test. Companies
like `SONOS INC` almost certainly have a very different funding/hiring
reality today than in 2014.

**Response (hard-stop, currently specified but not auto-enforced in
scoring):** any company flagged "stale" must be presented to the user with
an explicit warning — *"Funding data for this company is over 2 years old
and may not reflect current hiring reality — verify independently before
prioritizing this company"* — rather than being folded into the same "Top"
label as a company with genuinely recent funding. **This is not yet coded
into `score_companies.py`'s tier logic itself** — it is currently a
separate check (`funding_recency.py`) run alongside the main tool. Fully
integrating it as an automatic score penalty is named here as an open
next step, not silently treated as done.
## Gate Summary Table (response + who resolves)

| Gate | Trigger condition | Response | Who resolves |
|---|---|---|---|
| Liveness | `check-liveness.mjs` returns `expired` | **Block** — remove from recommendation list entirely | Tool auto-resolves (no human time wasted on a confirmed-dead posting) |
| Liveness | `check-liveness.mjs` returns `uncertain` | **Flag** — surface to user with a warning, do not auto-approve or auto-reject | The job-seeker (user) — must manually open the link and confirm before applying |
| Funding recency | Last funding round > 2 years old | **Flag** — attach an explicit "stale funding" warning to the company's tier label | The job-seeker (user) — must independently verify the company's current hiring activity before treating it as equal to a fresh-funding "Top" company |
| Funding recency | Last funding round <= 2 years old | **Approve** — no warning attached, score stands as computed | Tool auto-resolves |
## Why Both Gates Are Non-Negotiable

Neither gate touches money or legal status directly, but both gate a
**scarce, irreplaceable resource: the person's limited application-writing
time during an OPT/STEM-OPT window with a hard deadline.** Recommending
effort toward a dead posting or a company whose funding reality is 12
years stale spends that resource on a false signal. Per the assignment's
own framing, this is exactly the kind of reallocation error that "does not
crash visibly" — the tool still runs, still outputs a clean-looking score,
and still feels authoritative, while quietly wasting the one resource this
entire tool exists to protect.