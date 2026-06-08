"""
DropoffDesk — Synthetic Data Generator
Generates 1,800 candidates and associated hiring pipeline data
with intentional data quality issues for cleaning practice.
"""

import pandas as pd
import random
from faker import Faker
from datetime import date, timedelta
import os

fake = Faker('en_IN')   # Indian locale for realistic names
random.seed(42)          # Makes results reproducible — same data every run
Faker.seed(42)

# ── CONSTANTS ────────────────────────────────────────────────────────────────

START_DATE = date(2023, 1, 1)
END_DATE   = date(2024, 6, 30)    # 18 months of data

DEPARTMENTS   = ['Engineering', 'Marketing', 'Sales', 'Product', 'Operations', 'Finance']
ROLE_LEVELS   = ['Junior', 'Mid', 'Senior', 'Lead']
PIPELINE_STAGES = [
    'Application Review',
    'Phone Screen',
    'Technical Assessment',
    'Hiring Manager Interview',
    'Final Round',
    'Offer Extended'
]
REJECTION_REASONS = [
    'Insufficient experience',
    'Failed technical assessment',
    'Culture mismatch',
    'Salary expectations too high',
    'No-show',
    'Role cancelled',
    None   # <-- intentionally NULL for 23% of rejections
]
SALARY_BANDS = ['Band 1', 'Band 2', 'Band 3', 'Band 4', 'Band 5']

# Intentional data quality issue: 11 variants of "LinkedIn"
SOURCE_CHANNELS = [
    'LinkedIn', 'linkedin', 'LI', 'Linked In', 'linkedin.com',   # 5 LinkedIn variants
    'LinkedIn ', ' LinkedIn', 'LINKEDIN', 'Linkedin', 'linked in', 'LinkedIn.com',  # 6 more
    'Naukri', 'Indeed', 'Employee Referral', 'Company Website',
    'Campus Placement', 'Instagram', 'Glassdoor'
]
# Weighted so LinkedIn variants make up ~40% of records
SOURCE_WEIGHTS = [8,4,2,2,2,2,2,2,2,2,2, 15,12,10,8,5,3,3]

def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))

# ── GENERATE RECRUITERS ───────────────────────────────────────────────────────
# Small team of 8 recruiters — we want to be able to spot recruiter-level variance

def generate_recruiters(n=8):
    rows = []
    for i in range(1, n+1):
        rows.append({
            'recruiter_id': i,
            'name': fake.name(),
            'team': random.choice(['Tech Hiring', 'Business Hiring']),
            'join_date': random_date(date(2020, 1, 1), date(2023, 6, 1)),
            'region': random.choice(['Bangalore', 'Mumbai', 'Delhi', 'Hyderabad'])
        })
    return pd.DataFrame(rows)

# ── GENERATE ROLES ────────────────────────────────────────────────────────────

def generate_roles(n=30):
    rows = []
    for i in range(1, n+1):
        open_d = random_date(START_DATE, date(2024, 3, 1))
        closed_d = open_d + timedelta(days=random.randint(20, 120)) if random.random() > 0.3 else None
        rows.append({
            'role_id': i,
            'title': f"{random.choice(ROLE_LEVELS)} {random.choice(['Engineer','Analyst','Manager','Designer','Specialist'])}",
            'department': random.choice(DEPARTMENTS),
            'level': random.choice(ROLE_LEVELS),
            'headcount_target': random.randint(1, 4),
            'open_date': open_d,
            'closed_date': closed_d
        })
    return pd.DataFrame(rows)

# ── GENERATE CANDIDATES ───────────────────────────────────────────────────────

def generate_candidates(n=1800):
    rows = []
    for i in range(1, n+1):
        rows.append({
            'candidate_id': i,
            'name': fake.name(),
            'source_channel': random.choices(SOURCE_CHANNELS, weights=SOURCE_WEIGHTS)[0],
            'application_date': random_date(START_DATE, END_DATE),
            'role_level': random.choice(ROLE_LEVELS),
            'department': random.choice(DEPARTMENTS)
        })

    # ── DATA QUALITY ISSUE 1: Duplicate candidate_ids from CRM migration at Month 7
    # Months 7-8 (July-August 2023): 40 candidates get duplicate entries
    duplicates = random.sample(range(1, 300), 40)
    dup_rows = []
    for cid in duplicates:
        existing = next(r for r in rows if r['candidate_id'] == cid)
        dup = existing.copy()
        dup['application_date'] = existing['application_date'] + timedelta(days=random.randint(1, 3))
        dup_rows.append(dup)
    rows.extend(dup_rows)

    # ── DATA QUALITY ISSUE 2: 3 orphaned candidates — will have no pipeline_events
    # We track these IDs so pipeline generation can skip them
    orphan_ids = random.sample(range(1600, 1800), 3)

    df = pd.DataFrame(rows)
    return df, orphan_ids

# ── GENERATE PIPELINE EVENTS ──────────────────────────────────────────────────

def generate_pipeline_events(candidates_df, orphan_ids, recruiters_df):
    rows = []
    event_id = 1

    for _, candidate in candidates_df.drop_duplicates('candidate_id').iterrows():
        cid = candidate['candidate_id']

        # Skip orphaned candidates — they have no events (data quality issue 3)
        if cid in orphan_ids:
            continue

        # Each candidate goes through stages until they fail or pass all
        current_date = candidate['application_date'] + timedelta(days=random.randint(1, 3))
        recruiter_id = random.choice(recruiters_df['recruiter_id'].tolist())

        # Recruiters 3 and 7 are intentionally slow (creates the bottleneck we'll find)
        if recruiter_id in [3, 7]:
            stage_delay_multiplier = 2.5
        else:
            stage_delay_multiplier = 1.0

        for stage in PIPELINE_STAGES:
            # 35% chance of failing at each stage (except first — all pass review briefly)
            fail_prob = 0.15 if stage == 'Application Review' else 0.35

            if random.random() < fail_prob:
                # Candidate fails this stage
                outcome = 'fail'
                reject_reason = random.choices(
                    REJECTION_REASONS,
                    weights=[15, 20, 10, 10, 8, 7, 30]   # 30% weight on None
                )[0]
            else:
                outcome = 'pass'
                reject_reason = None

            # DATA QUALITY ISSUE 4: Inconsistent date formats (we'll store as string for 15% of records)
            # We actually store dates properly here; the "issue" will be in a separate badly-formatted CSV
            rows.append({
                'event_id': event_id,
                'candidate_id': cid,
                'stage_name': stage,
                'event_date': current_date,
                'recruiter_id': recruiter_id,
                'outcome': outcome,
                'reject_reason': reject_reason
            })
            event_id += 1

            if outcome == 'fail':
                break

            # Time between stages — slow recruiters take longer
            base_days = random.randint(2, 8)
            current_date += timedelta(days=int(base_days * stage_delay_multiplier))

    return pd.DataFrame(rows)

# ── GENERATE OFFERS ───────────────────────────────────────────────────────────

def generate_offers(pipeline_df, candidates_df):
    # Only candidates who passed the final stage get offers
    final_passers = pipeline_df[
        (pipeline_df['stage_name'] == 'Offer Extended') &
        (pipeline_df['outcome'] == 'pass')
    ]['candidate_id'].unique()

    rows = []
    offer_id = 1

    for cid in final_passers:
        last_event_date = pipeline_df[
            pipeline_df['candidate_id'] == cid
        ]['event_date'].max()

        offer_date = last_event_date + timedelta(days=random.randint(1, 5))
        offer_expiry = offer_date + timedelta(days=7)
        accepted = random.random() < 0.68   # 68% acceptance — drops to ~54% in Q4 (we'll build this in)
        join_date = offer_date + timedelta(days=random.randint(14, 60)) if accepted else None

        # DATA QUALITY ISSUE 5: 6% of records have offer_date AFTER join_date (data entry error)
        if accepted and random.random() < 0.06:
            offer_date, join_date = join_date, offer_date   # swap them — this is the bug

        rows.append({
            'offer_id': offer_id,
            'candidate_id': int(cid),
            'offer_date': offer_date,
            'offer_expiry': offer_expiry,
            'accepted': accepted,
            'join_date': join_date,
            'salary_band': random.choice(SALARY_BANDS)
        })
        offer_id += 1

    return pd.DataFrame(rows)

# ── MAIN: RUN EVERYTHING AND SAVE ─────────────────────────────────────────────

if __name__ == '__main__':
    print("Generating recruiters...")
    recruiters = generate_recruiters()

    print("Generating roles...")
    roles = generate_roles()

    print("Generating candidates (with intentional quality issues)...")
    candidates, orphan_ids = generate_candidates(1800)

    print(f"Generating pipeline events (orphaning candidate IDs: {orphan_ids})...")
    pipeline = generate_pipeline_events(candidates, orphan_ids, recruiters)

    print("Generating offers...")
    offers = generate_offers(pipeline, candidates)

    # Save all to CSV
    os.makedirs('../data/raw', exist_ok=True)
    recruiters.to_csv('../data/raw/recruiters.csv', index=False)
    roles.to_csv('../data/raw/roles.csv', index=False)
    candidates.to_csv('../data/raw/candidates.csv', index=False)
    pipeline.to_csv('../data/raw/pipeline_events.csv', index=False)
    offers.to_csv('../data/raw/offers.csv', index=False)

    print("\n✅ Done! Summary:")
    print(f"  Recruiters:      {len(recruiters):,} rows")
    print(f"  Roles:           {len(roles):,} rows")
    print(f"  Candidates:      {len(candidates):,} rows (includes duplicates)")
    print(f"  Pipeline events: {len(pipeline):,} rows")
    print(f"  Offers:          {len(offers):,} rows")
    print(f"\nOrphaned candidate IDs (no events): {orphan_ids}")
    print("Raw CSVs saved to data/raw/")