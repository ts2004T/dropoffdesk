# Data Quality Log — DropoffDesk

## Analyst: Tanishka Suryawanshi

## Last Updated: June 2026

---

## Purpose

This log documents every data quality issue found in the raw hiring pipeline data,
the root cause of each issue, the scale of impact, and the resolution decision.
This is an analyst deliverable — it proves the data was interrogated, not just used.

---

## Issue 001 — Duplicate candidate_ids from CRM migration

**Table:** candidates
**Column:** candidate_id
**Root Cause:** CRM system migration in Month 7 (July 2023) re-imported existing
candidates without deduplication checks
**Scale:** ~40 duplicate records
**Resolution:** Keep the earliest record (lowest application_date). Drop duplicates
using pandas sort + drop_duplicates(keep='first').
**Why this approach:** The earlier record is the original application. The later
duplicate is the migration artifact.

---

## Issue 002 — source_channel has 11 variants of "LinkedIn"

**Table:** candidates
**Column:** source_channel
**Root Cause:** No dropdown enforcement in the ATS — recruiters typed values manually
**Scale:** ~40% of all candidate records affected
**Resolution:** Standardise all variants to "LinkedIn" using lowercase + trim + LIKE
matching. Any value containing "linkedin" or equal to "li" or "linked in" → "LinkedIn"
**Why this approach:** All variants unambiguously refer to the same channel.
Standardising is required for accurate source ROI analysis.

---

## Issue 003 — Orphaned candidates with no pipeline events

**Table:** candidates / pipeline_events
**Column:** candidate_id
**Root Cause:** CRM sync failure — 3 candidates were created in the system but
their application events were never recorded
**Scale:** 3 candidates (IDs: 1723, 1633, 1644)
**Resolution:** Keep in candidates table. Add a boolean flag column `has_events`.
Do NOT delete — their absence from pipeline is itself analytically meaningful.
**Why this approach:** Deleting them would hide a data integrity problem.
Flagging preserves them for audit while excluding them from funnel calculations.

---

## Issue 004 — NULL reject_reason for ~23% of failed pipeline events

**Table:** pipeline_events
**Column:** reject_reason
**Root Cause:** Recruiters did not fill in rejection reason when marking candidates
as failed — no mandatory field enforcement in the ATS
**Scale:** ~23% of all failure records
**Resolution:** Do NOT impute. Replace NULL with "Not Provided" as a label.
Track the NULL rate as a data quality metric in its own right.
**Why this approach:** Guessing a rejection reason would introduce false data.
The absence of a reason is itself a finding — it indicates poor data discipline
that the HR team should address.

---

## Issue 005 — offer_date recorded after join_date for ~6% of offer records

**Table:** offers
**Columns:** offer_date, join_date
**Root Cause:** Manual data entry error — recruiter entered the join date in the
offer_date field and vice versa
**Scale:** ~6% of accepted offer records
**Resolution:** Flag with a boolean column `date_inversion_flag = True`.
Do NOT auto-correct. Log for stakeholder review.
**Why this approach:** We cannot know which date is correct without checking the
original offer letter. Auto-correcting would introduce assumptions into the data.
Flagging lets the business owner verify and correct at source.

---

## Summary Table

| Issue                          | Table           | Scale            | Action Taken                     |
| ------------------------------ | --------------- | ---------------- | -------------------------------- |
| 001 — Duplicate candidate_ids  | candidates      | ~40 rows         | Deduplicated, kept earliest      |
| 002 — LinkedIn source variants | candidates      | ~40% of rows     | Standardised to "LinkedIn"       |
| 003 — Orphaned candidates      | candidates      | 3 rows           | Flagged with has_events column   |
| 004 — NULL reject_reason       | pipeline_events | ~23% of failures | Labelled "Not Provided"          |
| 005 — Date inversions          | offers          | ~6% of offers    | Flagged with date_inversion_flag |
