"""
GIGO Gate — Skeptical EDA for SEC_DOL_H1b_data_mapped.csv
Assignment: The Reallocation Engine, Audited
Run with: python gigo_eda.py
"""

import csv

PATH = r"data\80-days-to-stay\data\SEC_DOL_H1b_data_mapped.csv"

def is_blank(v):
    return v is None or v.strip() == ""

total = 0
blank_titles = 0
blank_approvals = 0
ages_with_titles = []
ages_without_titles = []
company_names = []
funding_dates = []
duplicate_check = {}

with open(PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        total += 1
        name = row.get("company_name", "").strip().upper()
        company_names.append(name)
        duplicate_check[name] = duplicate_check.get(name, 0) + 1

        titles = row.get("top_job_titles_sponsored", "")
        approvals = row.get("Total Approvals", "")

        age_raw = row.get("company_age_years", "")
        try:
            age = float(age_raw)
        except ValueError:
            age = None

        if is_blank(titles):
            blank_titles += 1
            if age is not None:
                ages_without_titles.append(age)
        else:
            if age is not None:
                ages_with_titles.append(age)

        if is_blank(approvals):
            blank_approvals += 1

        fd = row.get("latest_funding_date", "")
        if not is_blank(fd):
            funding_dates.append(fd)

print("=== FIELD INVENTORY ===")
print(f"Columns found: {fieldnames}")
print(f"Is there a 'data pulled on' / snapshot-date field? -> {'snapshot_date' in fieldnames or 'data_pulled_on' in fieldnames}")
print()

print("=== ROW COUNT ===")
print(f"Total data rows: {total}")
print()

print("=== SPONSORSHIP HISTORY BLANKS ===")
print(f"Rows with BLANK top_job_titles_sponsored: {blank_titles} ({blank_titles/total*100:.1f}%)")
print(f"Rows with BLANK Total Approvals: {blank_approvals} ({blank_approvals/total*100:.1f}%)")
print()

print("=== COMPANY AGE: WITH vs WITHOUT sponsorship history ===")
if ages_with_titles:
    print(f"Companies WITH sponsorship titles  — n={len(ages_with_titles)}, "
          f"avg age = {sum(ages_with_titles)/len(ages_with_titles):.1f} years")
if ages_without_titles:
    print(f"Companies WITHOUT sponsorship titles — n={len(ages_without_titles)}, "
          f"avg age = {sum(ages_without_titles)/len(ages_without_titles):.1f} years")
print()

print("=== DUPLICATE COMPANY NAMES ===")
dupes = {k: v for k, v in duplicate_check.items() if v > 1 and k != ""}
print(f"Number of company names appearing more than once: {len(dupes)}")
if dupes:
    sample = list(dupes.items())[:5]
    print(f"Sample duplicates: {sample}")
print()

print("=== FUNDING DATE FORMAT CHECK ===")
sample_dates = funding_dates[:5]
print(f"Sample latest_funding_date values: {sample_dates}")