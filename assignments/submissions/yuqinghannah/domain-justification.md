# Domain Justification — ux-designer-sponsor-triage
**Who / situation:** An international UX/Product Design graduate student on
STEM OPT (graduating August 2026), applying to Product Designer and UX
Designer roles, for whom H-1B sponsorship is a hard requirement rather than
a preference.
**Information asymmetry:** A job posting for "Product Designer" almost never
states whether the company will sponsor a visa for that specific hire.
Public H-1B petition history exists (DOL/USCIS records), but it is not
organized by job-title text an applicant could search in minutes — it takes
digging through raw government filings most applicants never attempt before
spending hours polishing an application. This mode surfaces that signal —
whether a company has *literally* sponsored a designer-titled role before —
before application time is spent, not after an offer is already at risk. A
second, related asymmetry: an applicant cannot easily tell whether a posting
they found is still accepting applications, or whether a company's funding
is stale enough that it may no longer be actively hiring — both of which
this revision now checks with real scripts rather than eyeballing.
**Engine layers:** Primarily "80 Days to Stay" (the `SEC_DOL_H1b_data_mapped.csv`
join of Form D funding data and H-1B history), with a Job-Ops liveness check
layered on top so time isn't spent on postings that are no longer accepting
applications.
**Failure modes:**
1. **Title-string blindness.** The mode matches literally on the
   `top_job_titles_sponsored` field. A company that has sponsored an
   "Interaction Designer" or "Design Technologist" role will not be caught by
   a search for "UX Designer" or "Product Designer," even though it is
   functionally the same job family. This under-counts real matches and is
   hardest to catch for an applicant who is new to how varied design titles
   are across companies — they may see "no match" and wrongly conclude a
   company has never sponsored a designer at all, when it sponsored one
   under a different title.
2. **Survivorship in sponsorship history.** A company with zero prior H-1B
   filings for *any* design title (but filings for engineering roles) could
   read as "won't sponsor design," when it may simply never have hired a
   sponsored designer yet — design teams are often smaller and newer than
   engineering teams at a given company. This under-scores small but
   genuinely willing companies. It is hardest to catch for an applicant who
   treats a "no history" result as a hard no rather than a "worth asking
   directly" flag, since the absence of a filing looks identical whether it
   reflects unwillingness or simply low sample size.
3. **Intuition-vs-reality gap on liveness, and an unvalidated funding
   threshold.** Prior to this revision, both the liveness gate and the
   funding-recency gate were "eyeballed," not scripted — this mode's own
   Worked Run shows why that's dangerous. I assumed a posting from ~1 month
   ago (Clutch) would likely be expired; a real Playwright check showed it
   was still active. I assumed a different posting (Hagerty) was probably
   still live; the real check showed it had expired. Human intuition about
   posting age was wrong in both directions on a 3-URL sample. Separately,
   the funding-recency thresholds this mode now uses (≤18mo fresh / 18–30mo
   aging / >30mo stale) are my own judgment call, not a number the book or
   this repo's docs pin anywhere — a company's actual hiring runway after a
   funding round varies by industry, headcount, and burn rate in ways this
   fixed threshold cannot see. This failure is hardest to catch for an
   applicant who trusts a "fresh funding" or "still live" verdict at face
   value without knowing the threshold is a guess, not a fact — they would
   have no way to tell a genuinely-verified-fresh company from one that
   merely cleared an arbitrary cutoff.