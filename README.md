# DropoffDesk — Hiring Funnel Intelligence Platform

![Project Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard-yellow)

A full-stack data analytics project investigating a 23% offer acceptance rate decline and 46% time-to-hire increase across a fictional company's hiring pipeline — using PostgreSQL, Python, statistical testing, and Power BI, with a 6-month pipeline velocity forecast.

---

## The Business Problem

A talent acquisition team saw offer acceptance rates drop 23% in Q4 and time-to-hire balloon from 28 to 41 days in engineering roles. No one knew why.

This project answers five key questions:

1. At which pipeline stage are candidates being lost — and which recruiters have the worst conversion?
2. Where is time being lost in the hiring process, and is it recruiter-specific or pipeline-wide?
3. Which sourcing channels deliver the highest quality candidates, not just the highest volume?
4. Is the time-to-hire increase concentrated in Engineering, or is it a company-wide trend?
5. At current pipeline velocity, will Q3 headcount targets be met?

---

## Key Findings

| Finding                | Detail                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------ |
| **TTH bottleneck**     | Two recruiters process candidates 2–3× slower than peers despite equal workload      |
| **Slowest recruiter**  | Jhanvi Chaudhary — median 24 days vs team average of 8–9 days                        |
| **Bottleneck stage**   | Technical Screening median increased from 4 → 11 days in Q4                          |
| **Acceptance decline** | NOT correlated with recruiter speed — r = 0.046 (p > 0.05)                           |
| **TTH significance**   | Engineering vs non-Engineering TTH: p < 0.05 — department-specific, not company-wide |
| **Best channel**       | Employee Referrals and Direct Applications show highest Source Quality Index         |
| **Forecast risk**      | Q3 headcount targets at risk if screening bottleneck persists                        |

---

## Dashboard Preview

### Executive Summary

![Executive Summary](docs/executive_summary.png)

### Source Channel ROI

![Source Channel ROI](docs/source_channel_roi.png)

### Funnel Analysis

![Funnel Analysis](docs/funnel_analysis.png)

### Recruiter Performance

![Recruiter Performance](docs/recruiter_performance.png)

---

## Project Architecture

```text
dropoffdesk/
├── data/
│   ├── raw/                          # Generated CSVs — excluded from Git
│   └── clean/                        # Cleaned datasets after pipeline
├── notebooks/
│   ├── generate_data.py              # Synthetic data generator (Faker, 1,800 candidates)
│   ├── clean_pipeline.py             # Data cleaning pipeline
│   ├── import_to_postgres.py         # PostgreSQL loader — excluded from Git
│   ├── stats_analysis.ipynb          # t-test, chi-square, Pearson correlation
│   └── forecast.ipynb                # Linear regression pipeline velocity forecast
├── sql/
│   ├── schema.sql                    # 5-table normalised schema with CASCADE drops
│   └── analysis.sql                  # 8 core business queries
├── dashboard/
│   └── DropoffDesk.pbix              # Power BI dashboard — 4 pages, DAX measures
├── docs/
│   ├── data_quality_log.md           # Every data issue, root cause, and resolution
│   ├── business_memo.md              # Analyst memo to HR VP
│   ├── business_memo.pdf             # PDF export
│   └── forecast_chart.png            # 6-month pipeline velocity projection
├── .gitignore
└── README.md
```

---

## Tech Stack

| Tool                 | Purpose                                                                      |
| -------------------- | ---------------------------------------------------------------------------- |
| **PostgreSQL**       | Primary data store — 5-table normalised schema                               |
| **Python 3.12**      | Synthetic data generation, cleaning pipeline, statistical tests, forecasting |
| **pandas / numpy**   | Data manipulation and cleaning                                               |
| **scipy**            | Statistical testing (t-test, chi-square, Pearson correlation)                |
| **scikit-learn**     | Linear regression forecasting model                                          |
| **matplotlib**       | Forecast visualisation                                                       |
| **SQLAlchemy**       | PostgreSQL connection and data loading                                       |
| **Power BI Desktop** | 4-page interactive dashboard with DAX measures                               |
| **Git / GitHub**     | Version control                                                              |

---

## Data

**Source:** Synthetic data generated with Python Faker — designed to mirror real HR system data quality issues  
**Coverage:** 18 months of hiring pipeline data, 1,800 candidates  
**Schema:** 5 related tables — candidates, pipeline_events, recruiters, offers, roles  
**Intentional quality issues built in:**

| Issue                               | Simulated Root Cause        | Cleaning Technique                      |
| ----------------------------------- | --------------------------- | --------------------------------------- |
| 40 duplicate candidate_ids          | CRM migration in Month 7    | Deduplication — keep earliest record    |
| 11 LinkedIn source_channel variants | No ATS dropdown enforcement | String standardisation via LOWER + TRIM |
| 3 orphaned candidates               | CRM sync failure            | Flagged with `has_events` boolean       |
| NULL reject_reason (~23%)           | Lazy recruiter data entry   | Labelled "Not Provided" — not imputed   |
| offer_date after join_date (6%)     | Manual data entry error     | Flagged with `date_inversion_flag`      |

Full documentation: [`docs/data_quality_log.md`](docs/data_quality_log.md)

> Raw data files and the PostgreSQL import script are excluded from this repository. The cleaning pipeline documents all transformations applied.

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

## How to Run

**1. Clone the repo**

```bash
git clone https://github.com/ts2004T/dropoffdesk.git
cd dropoffdesk
```

**2. Create and activate virtual environment**

```bash
python -m venv venv
venv\Scripts\activate.bat        # Windows
```

**3. Install dependencies**

```bash
pip install faker pandas sqlalchemy psycopg2-binary scipy scikit-learn matplotlib
```

**4. Generate and clean data**

```bash
cd notebooks
python generate_data.py
python clean_pipeline.py
```

**5. Load to PostgreSQL**

```bash
# Create your own import_to_postgres.py using the schema in sql/schema.sql
# Connection string: postgresql://postgres:YOUR_PASSWORD@localhost:5432/dropoffdesk
```

**6. Run SQL analysis**

Open `sql/analysis.sql` in DBeaver connected to the `dropoffdesk` database.

**7. Run notebooks in order**

1. `notebooks/stats_analysis.ipynb`
2. `notebooks/forecast.ipynb`

---

## Business Recommendations

Five actionable recommendations derived from the analysis:

1. **Implement a 5-day SLA on Technical Screening** — flag candidates uncontacted after 3 days; coaching for the two bottleneck recruiters is the single highest-leverage action available
2. **Deploy an offer-decline exit survey** — 3 questions on compensation expectations, timeline experience, and competing offer; the acceptance decline cannot be diagnosed without candidate-side signal
3. **Reallocate LinkedIn budget to referrals** — Employee Referrals and Direct Applications show 2× higher Source Quality Index than paid social channels
4. **Address Engineering-specific TTH** — the increase is statistically significant in Engineering only (p < 0.05); a blanket company-wide policy response would be misdirected
5. **Q3 headcount risk — act now** — at current pipeline velocity, open roles will not be filled before quarter end; the screening bottleneck is the only controllable variable

Full analysis: [docs/business_memo.md](docs/business_memo.md)

---

## Project Phases

- [x] Phase 1: Schema design & synthetic data generation
- [x] Phase 2: Data cleaning pipeline & quality log
- [x] Phase 3: SQL analysis — 8 core queries (funnel, TTH, source ROI, recruiter variance)
- [x] Phase 4: Statistical testing — t-test, chi-square, Pearson correlation
- [x] Phase 5: Pipeline velocity forecasting — linear regression, 6-month projection
- [x] Phase 6: Power BI dashboard — 4 pages, recruiter slicer, DAX measures
- [x] Phase 7: Business memo — Situation → Finding → Root Cause → Recommendation
- [x] Phase 8: GitHub cleanup & portfolio finalisation

---

## Author

**Tanishka Suryawanshi**  
BTech CSE from SRM University  
Bengaluru, India  
[LinkedIn](https://linkedin.com/in/your-linkedin) • [GitHub](https://github.com/ts2004T)

---

## Resume Bullet

> Built end-to-end hiring funnel analytics platform on PostgreSQL and Power BI, investigating a 23% offer acceptance rate decline across 1,800 synthetic candidates; identified recruiter-level TTH bottleneck (2–3× slower processing) via PERCENTILE_CONT SQL analysis and confirmed non-correlation with acceptance decline using Pearson r = 0.046; delivered 6-month pipeline velocity forecast and 5 actionable recommendations in a stakeholder memo.
