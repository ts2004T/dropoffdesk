# DropoffDesk — Hiring Funnel Intelligence Platform

> **End-to-end hiring pipeline analysis:** PostgreSQL schema design · Python data pipeline · SQL window functions · Statistical testing · Power BI dashboard · Executive memo

---

## The Business Problem

A talent acquisition team saw offer acceptance rates drop **23% in Q4** and time-to-hire balloon from **28 to 41 days** in engineering roles. No one knew why.

This project investigates the root cause using 18 months of hiring pipeline data — identifying recruiter-level bottlenecks, sourcing channel inefficiencies, and projecting whether Q3 headcount targets will be met at current pipeline velocity.

**The deliverable is not an app. It is an answer — backed by data.**

---

## Stakeholders

| Stakeholder                | Question Answered                                           |
| -------------------------- | ----------------------------------------------------------- |
| Head of Talent Acquisition | Which recruiters and channels are underperforming?          |
| HR VP                      | Why did offer acceptance decline and what should we do?     |
| Department Heads           | When will our open roles be filled?                         |
| CFO                        | Which sourcing channels cost the most and return the least? |

---

## KPIs Defined From Scratch

| KPI                      | Definition                                                   |
| ------------------------ | ------------------------------------------------------------ |
| Stage Conversion Rate    | % of candidates passing each pipeline stage                  |
| Median Time-in-Stage     | Median (not mean) days at each stage — resistant to outliers |
| Source Quality Index     | Offers extended / Applications from source                   |
| Offer Acceptance Rate    | % of offers accepted, trended monthly                        |
| Time-to-Hire (TTH)       | Days from application to accepted offer                      |
| Cost-per-Hire (estimate) | Sourcing channel volume × recruiter time proxy               |

---

## Tech Stack

| Tool                   | Role                                                |
| ---------------------- | --------------------------------------------------- |
| PostgreSQL             | Primary database — 5-table normalised schema        |
| Python (Faker, Pandas) | Synthetic data generation + cleaning pipeline       |
| scipy                  | Statistical tests (t-test, chi-square, correlation) |
| matplotlib             | Forecasting visualisation                           |
| Power BI + DAX         | 4-page stakeholder dashboard                        |
| Git + GitHub           | Version control                                     |

---

## Project Architecture

```
Raw Synthetic Data (Faker + Python, 1,800 candidates, 18 months)
        ↓
PostgreSQL — 5-table normalised schema
        ↓
Python Cleaning Pipeline (Pandas) — dedup, standardise, flag
        ↓
SQL Analyses — 8 core queries (funnel, TTH, source ROI, recruiter variance)
        ↓
Statistical Tests — t-test, chi-square, correlation (Python / scipy)
        ↓
Forecasting — pipeline velocity regression, 6-month projection
        ↓
Power BI Dashboard — 4 pages, recruiter slicer, DAX measures
        ↓
Business Memo (PDF) — Situation → Finding → Root Cause → Recommendation
```

---

## Repository Structure

```
dropoffdesk/
├── sql/
│   ├── schema.sql              # 5-table normalised schema
│   ├── cleaning.sql            # SQL cleaning queries
│   └── analysis.sql            # 8 core business queries (in progress)
│
├── notebooks/
│   ├── generate_data.py        # Synthetic data generator with intentional quality issues
│   ├── clean_pipeline.py       # Data cleaning pipeline
│   ├── import_to_postgres.py   # Loads clean CSVs into PostgreSQL
│   ├── stats_analysis.ipynb    # Statistical testing (coming)
│   └── forecast.ipynb          # Hiring forecast model (coming)
│
├── data/
│   ├── raw/                    # Original generated CSVs (not committed to Git)
│   ├── clean/                  # Cleaned versions after pipeline
│   └── reference/              # Benchmark references
│
├── dashboard/
│   └── DropoffDesk.pbix        # Power BI dashboard (coming)
│
├── docs/
│   ├── data_quality_log.md     # Every data issue found, root cause, and resolution
│   └── business_memo.pdf       # 1-page analyst memo to HR VP (coming)
│
└── README.md
```

---

## Dataset

**Synthetic data generated using Python Faker** — 1,800 candidates across 18 months with 5 related tables. Real HR data is private; interviewers expect synthetic data for this domain and evaluate the schema design and cleaning complexity instead.

**Intentional data quality issues built in:**

| Issue                           | Root Cause Simulated           | Cleaning Technique                      |
| ------------------------------- | ------------------------------ | --------------------------------------- |
| 40 duplicate candidate_ids      | CRM migration in Month 7       | Deduplication — keep earliest record    |
| 11 variants of "LinkedIn"       | No dropdown enforcement in ATS | String standardisation via LOWER + TRIM |
| 3 orphaned candidates           | CRM sync failure               | Flagged with `has_events` boolean       |
| NULL reject_reason (~23%)       | Lazy recruiter data entry      | Labelled "Not Provided" — not imputed   |
| offer_date after join_date (6%) | Manual data entry error        | Flagged with `date_inversion_flag`      |

Full documentation: [`docs/data_quality_log.md`](docs/data_quality_log.md)

---

## Database Schema

```sql
candidates(candidate_id, name, source_channel, application_date, role_level, department)
pipeline_events(event_id, candidate_id, stage_name, event_date, recruiter_id, outcome, reject_reason)
recruiters(recruiter_id, name, team, join_date, region)
offers(offer_id, candidate_id, offer_date, offer_expiry, accepted, join_date, salary_band)
roles(role_id, title, department, level, headcount_target, open_date, closed_date)
```

---

## Progress

| Phase | Description                                            | Status         |
| ----- | ------------------------------------------------------ | -------------- |
| 1     | Schema design & synthetic data generation              | ✅ Complete    |
| 2     | Data cleaning pipeline & quality log                   | ✅ Complete    |
| 3     | SQL analysis — 8 core queries                          | 🔄 In Progress |
| 4     | Statistical analysis (t-test, chi-square, correlation) | ⬜ Pending     |
| 5     | Forecasting — pipeline velocity regression             | ⬜ Pending     |
| 6     | Power BI dashboard — 4 pages with DAX                  | ⬜ Pending     |
| 7     | Business memo — Situation → Finding → Recommendation   | ⬜ Pending     |
| 8     | GitHub cleanup & LinkedIn post                         | ⬜ Pending     |

---

## Key Findings

_To be completed as analysis progresses._

---

## Interview Talking Point

> "DropoffDesk started as a simple pipeline tracker idea, but the real analytical challenge was the question no one had answered: why did offer acceptance rates fall 23% in Q4? I designed a schema that captured stage-level events, recruiter attribution, and sourcing channels — deliberately built in the kinds of data quality issues real HR systems have, like inconsistent source labels and date entry errors. The core insight came from a PERCENTILE_CONT query that showed the median time in the technical screening stage had increased from 4 days to 11 days, concentrated in two recruiters. That's the kind of finding that changes a hiring manager's week."

---

## Running This Project

> Connection credentials are stored locally and not committed to Git.

**1. Generate data:**

```bash
cd notebooks
python generate_data.py
```

**2. Clean data:**

```bash
python clean_pipeline.py
```

**3. Load to PostgreSQL:**

```bash
python import_to_postgres.py
```

**4. Open `sql/analysis.sql` in DBeaver connected to `dropoffdesk` database**

---

## Author

**Tanishka Suryawanshi**  
Data Analytics Portfolio Project — 2026
