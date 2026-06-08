"""
DropoffDesk — Data Cleaning Pipeline
Reads raw CSVs, applies all fixes documented in data_quality_log.md,
saves clean versions to data/clean/
"""

import pandas as pd
import os

os.makedirs('../data/clean', exist_ok=True)

# ── LOAD RAW DATA ─────────────────────────────────────────────────────────────

print("Loading raw data...")
candidates = pd.read_csv('../data/raw/candidates.csv', parse_dates=['application_date'])
pipeline   = pd.read_csv('../data/raw/pipeline_events.csv', parse_dates=['event_date'])
offers     = pd.read_csv('../data/raw/offers.csv', parse_dates=['offer_date', 'join_date'])
recruiters = pd.read_csv('../data/raw/recruiters.csv', parse_dates=['join_date'])
roles      = pd.read_csv('../data/raw/roles.csv', parse_dates=['open_date', 'closed_date'])

# ── ISSUE 001: Deduplicate candidates ─────────────────────────────────────────

print("\n[Issue 001] Deduplicating candidates...")
before = len(candidates)
candidates = candidates.sort_values('application_date').drop_duplicates(
    subset='candidate_id', keep='first'
)
after = len(candidates)
print(f"  Removed {before - after} duplicate rows")
print(f"  Candidates remaining: {after:,}")

# ── ISSUE 002: Standardise source_channel ─────────────────────────────────────

print("\n[Issue 002] Standardising source_channel...")

def standardise_channel(ch):
    if pd.isna(ch):
        return 'Unknown'
    ch_clean = str(ch).lower().strip()
    if 'linkedin' in ch_clean or ch_clean in ['li', 'linked in']:
        return 'LinkedIn'
    return str(ch).strip()

before_unique = candidates['source_channel'].nunique()
candidates['source_channel'] = candidates['source_channel'].apply(standardise_channel)
after_unique = candidates['source_channel'].nunique()
print(f"  Unique source_channel values: {before_unique} → {after_unique}")
print(f"  LinkedIn count after standardisation: {(candidates['source_channel'] == 'LinkedIn').sum()}")

# ── ISSUE 003: Flag orphaned candidates ───────────────────────────────────────

print("\n[Issue 003] Flagging orphaned candidates...")
candidates_with_events = pipeline['candidate_id'].unique()
candidates['has_events'] = candidates['candidate_id'].isin(candidates_with_events)
orphan_count = (~candidates['has_events']).sum()
print(f"  Orphaned candidates flagged: {orphan_count}")

# ── ISSUE 004: Handle NULL reject_reason ──────────────────────────────────────

print("\n[Issue 004] Handling NULL reject_reason...")
null_before = pipeline['reject_reason'].isna().sum()
pipeline['reject_reason'] = pipeline['reject_reason'].fillna('Not Provided')
print(f"  NULLs replaced with 'Not Provided': {null_before}")
null_rate = null_before / len(pipeline[pipeline['outcome'] == 'fail']) * 100
print(f"  NULL rate among failures: {null_rate:.1f}%")

# ── ISSUE 005: Flag date inversions in offers ──────────────────────────────────

print("\n[Issue 005] Flagging offer/join date inversions...")
offers['date_inversion_flag'] = (
    offers['join_date'].notna() &
    (offers['join_date'] < offers['offer_date'])
)
inversion_count = offers['date_inversion_flag'].sum()
print(f"  Records flagged as date inversions: {inversion_count}")

# ── VALIDATION SUMMARY ────────────────────────────────────────────────────────

print("\n── Validation Summary ──────────────────────────────")
print(f"  candidates (clean):     {len(candidates):,} rows")
print(f"  pipeline_events:        {len(pipeline):,} rows")
print(f"  offers:                 {len(offers):,} rows")
print(f"    → date inversions:    {offers['date_inversion_flag'].sum()}")
print(f"  orphaned candidates:    {orphan_count}")
print(f"  source_channel unique:  {candidates['source_channel'].nunique()}")

# ── SAVE CLEAN DATA ───────────────────────────────────────────────────────────

print("\nSaving clean data...")
candidates.to_csv('../data/clean/candidates_clean.csv', index=False)
pipeline.to_csv('../data/clean/pipeline_events_clean.csv', index=False)
offers.to_csv('../data/clean/offers_clean.csv', index=False)
recruiters.to_csv('../data/clean/recruiters_clean.csv', index=False)
roles.to_csv('../data/clean/roles_clean.csv', index=False)
print("✅ All clean files saved to data/clean/")